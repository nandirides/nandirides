from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import SupportCategoryForm, SupportTicketForm
from .models import SupportCategory, SupportTicket, Notification, AuditLog
from django.urls import reverse
from django.http import JsonResponse

User = get_user_model()
def support_permission(permission):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            if request.user.is_superuser or request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        wrapper.__name__ = view_func.__name__
        wrapper.__doc__ = view_func.__doc__
        return wrapper
    return decorator
def create_audit_log(request, action, table_name, record_id=None, old_value=None, new_value=None):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
@login_required
@support_permission("support.view_supportticket")
def support_dashboard(request):
    tickets = SupportTicket.objects.select_related(
        "user",
        "category",
        "assigned_to",
        "ride",
    )
    total_tickets = tickets.count()
    open_tickets = tickets.filter(
        status=SupportTicket.Status.OPEN
    ).count()
    in_progress_tickets = tickets.filter(
        status=SupportTicket.Status.IN_PROGRESS
    ).count()
    resolved_tickets = tickets.filter(
        status=SupportTicket.Status.RESOLVED
    ).count()
    closed_tickets = tickets.filter(
        status=SupportTicket.Status.CLOSED
    ).count()
    urgent_tickets = tickets.filter(
        priority=SupportTicket.Priority.URGENT
    ).exclude(
        status=SupportTicket.Status.CLOSED
    ).count()
    high_tickets = tickets.filter(
        priority=SupportTicket.Priority.HIGH
    ).exclude(
        status=SupportTicket.Status.CLOSED
    ).count()
    medium_tickets = tickets.filter(
        priority=SupportTicket.Priority.MEDIUM
    ).exclude(
        status=SupportTicket.Status.CLOSED
    ).count()
    low_tickets = tickets.filter(
        priority=SupportTicket.Priority.LOW
    ).exclude(
        status=SupportTicket.Status.CLOSED
    ).count()
    recent_tickets = tickets.order_by("-created_at")[:8]
    categories = SupportCategory.objects.annotate(
        ticket_count=Count("support_tickets")
    ).order_by("-ticket_count", "name")[:6]
    agents = User.objects.filter(
        is_active=True,
        assigned_support_tickets__isnull=False,
    ).annotate(
        assigned_count=Count(
            "assigned_support_tickets",
            distinct=True,
        ),
        open_count=Count(
            "assigned_support_tickets",
            filter=Q(
                assigned_support_tickets__status=SupportTicket.Status.OPEN
            ),
            distinct=True,
        ),
        in_progress_count=Count(
            "assigned_support_tickets",
            filter=Q(
                assigned_support_tickets__status=SupportTicket.Status.IN_PROGRESS
            ),
            distinct=True,
        ),
        resolved_count=Count(
            "assigned_support_tickets",
            filter=Q(
                assigned_support_tickets__status=SupportTicket.Status.RESOLVED
            ),
            distinct=True,
        ),
    ).order_by("-assigned_count", "username")[:8]
    context = {
        "page_title": "Support Dashboard",
        "breadcrumb_items": [
            {
                "title": "Support Dashboard",
                "url": "support_dashboard", 
            },
        ],
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "urgent_tickets": urgent_tickets,
        "high_tickets": high_tickets,
        "medium_tickets": medium_tickets,
        "low_tickets": low_tickets,
        "recent_tickets": recent_tickets,
        "categories": categories,
        "agents": agents,
    }
    return render(
        request,
        "support/support_dashboard.html",
        context,
    )


@login_required
@support_permission("support.view_supportticket")
def ticket_list(request):
    tickets = SupportTicket.objects.select_related(
        "user",
        "category",
        "assigned_to",
        "ride",
    ).all()
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    priority = request.GET.get("priority", "").strip()
    category = request.GET.get("category", "").strip()
    if search:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search)
            | Q(subject__icontains=search)
            | Q(description__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
        )
    valid_statuses = {
        value for value, label in SupportTicket.Status.choices
    }
    valid_priorities = {
        value for value, label in SupportTicket.Priority.choices
    }
    if status in valid_statuses:
        tickets = tickets.filter(status=status)
    elif status:
        status = ""
    if priority in valid_priorities:
        tickets = tickets.filter(priority=priority)
    elif priority:
        priority = ""
    if category.isdigit():
        tickets = tickets.filter(category_id=category)
    elif category:
        category = ""
    tickets = tickets.order_by("-created_at")
    context = {
        "page_title": "Support Tickets",
        "breadcrumb_items": [
            {
                "title": "Support Tickets",
                "url": "ticket_list", 
            },
        ],
        "tickets": tickets,
        "categories": SupportCategory.objects.filter(
            is_active=True
        ).order_by("name"),
        "search": search,
        "selected_status": status,
        "selected_priority": priority,
        "selected_category": category,
        "status_choices": SupportTicket.Status.choices,
        "priority_choices": SupportTicket.Priority.choices,
    }
    return render(
        request,
        "support/ticket_list.html",
        context,
    )
@login_required
@support_permission("support.add_supportticket")
def ticket_form(request, pk=None):
    ticket = get_object_or_404(
        SupportTicket,
        pk=pk,
    ) if pk else None
    if ticket and not request.user.is_superuser and not request.user.has_perm(
        "support.change_supportticket"
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = SupportTicketForm(
            request.POST,
            instance=ticket,
        )
        if form.is_valid():
            with transaction.atomic():
                is_update = ticket is not None
                old_status = ticket.status if ticket else None
                old_priority = ticket.priority if ticket else None
                old_assigned_to = ticket.assigned_to_id if ticket else None
                ticket = form.save(commit=False)
                if ticket.status == SupportTicket.Status.CLOSED:
                    if not ticket.closed_at:
                        ticket.closed_at = timezone.now()
                else:
                    ticket.closed_at = None
                ticket.save()
                create_audit_log(
                    request=request,
                    action="UPDATE" if is_update else "CREATE",
                    table_name="support_supportticket",
                    record_id=ticket.pk,
                    old_value={
                        "status": old_status,
                        "priority": old_priority,
                        "assigned_to": old_assigned_to,
                    } if is_update else None,
                    new_value={
                        "status": ticket.status,
                        "priority": ticket.priority,
                        "assigned_to": ticket.assigned_to_id,
                        "ticket_number": ticket.ticket_number,
                    },
                )
                Notification.objects.create(
                    user=ticket.user,
                    notification_type="support_ticket",
                    title=(
                        "Support Ticket Updated"
                        if is_update
                        else "Support Ticket Created"
                    ),
                    message=(
                        f"Your support ticket {ticket.ticket_number} has "
                        f"{'been updated' if is_update else 'been created'} successfully."
                    ),
                    reference_type="support_ticket",
                    reference_id=ticket.pk,
                )
            messages.success(
                request,
                f"Ticket {ticket.ticket_number} "
                f"{'updated' if is_update else 'created'} successfully.",
            )
            return redirect(
                "ticket_detail",
                pk=ticket.pk,
            )
    else:
        form = SupportTicketForm(
            instance=ticket,
        )
    context = {
        "page_title": "Edit Ticket" if ticket else "Create Ticket",
        "breadcrumb_items": [
            {
                "title": "Tickets",
                "url": reverse("ticket_list"),
            },
            {
                "title": "Edit Ticket" if ticket else "Create Ticket",
                "url": (
                    reverse("ticket_edit", args=[ticket.id])
                    if ticket
                    else reverse("ticket_add")
                ),
            },
        ],
        "form": form,
        "ticket": ticket,
    }
    return render(
        request,
        "support/ticket_form.html",
        context,
    )
@login_required
@support_permission("support.view_supportticket")
def ticket_detail(request, pk):
    ticket = get_object_or_404(
        SupportTicket.objects.select_related(
            "user",
            "category",
            "assigned_to",
            "ride",
        ),
        pk=pk,
    )
    if request.method == "POST":
        if not request.user.is_superuser and not request.user.has_perm(
            "support.change_supportticket"
        ):
            raise PermissionDenied
        action = request.POST.get("action", "").strip()
        if action == "change_status":
            new_status = request.POST.get("status", "").strip()
            valid_statuses = {
                value for value, label in SupportTicket.Status.choices
            }
            if new_status not in valid_statuses:
                messages.error(request, "Invalid ticket status.")
                return redirect("ticket_detail", pk=pk)
            old_status = ticket.status
            ticket.status = new_status
            if new_status == SupportTicket.Status.CLOSED:
                if not ticket.closed_at:
                    ticket.closed_at = timezone.now()
            else:
                ticket.closed_at = None
            ticket.save()
            create_audit_log(
                request=request,
                action="STATUS_CHANGE",
                table_name="support_supportticket",
                record_id=ticket.pk,
                old_value={"status": old_status},
                new_value={"status": ticket.status},
            )
            Notification.objects.create(
                user=ticket.user,
                notification_type="support_ticket",
                title="Ticket Status Updated",
                message=(
                    f"Ticket {ticket.ticket_number} status changed to "
                    f"{ticket.get_status_display()}."
                ),
                reference_type="support_ticket",
                reference_id=ticket.pk,
            )
            messages.success(
                request,
                f"Ticket status changed to {ticket.get_status_display()}.",
            )
            return redirect("ticket_detail", pk=pk)
        if action == "change_priority":
            new_priority = request.POST.get("priority", "").strip()
            valid_priorities = {
                value for value, label in SupportTicket.Priority.choices
            }
            if new_priority not in valid_priorities:
                messages.error(request, "Invalid ticket priority.")
                return redirect("ticket_detail", pk=pk)
            old_priority = ticket.priority
            ticket.priority = new_priority
            ticket.save()
            create_audit_log(
                request=request,
                action="PRIORITY_CHANGE",
                table_name="support_supportticket",
                record_id=ticket.pk,
                old_value={"priority": old_priority},
                new_value={"priority": ticket.priority},
            )
            Notification.objects.create(
                user=ticket.user,
                notification_type="support_ticket",
                title="Ticket Priority Updated",
                message=(
                    f"Ticket {ticket.ticket_number} priority changed to "
                    f"{ticket.get_priority_display()}."
                ),
                reference_type="support_ticket",
                reference_id=ticket.pk,
            )
            messages.success(
                request,
                f"Ticket priority changed to {ticket.get_priority_display()}.",
            )
            return redirect("ticket_detail", pk=pk)
        if action == "assign_ticket":
            assigned_id = request.POST.get("assigned_to", "").strip()
            assigned_user = None
            if assigned_id:
                assigned_user = get_object_or_404(
                    User,
                    pk=assigned_id,
                    is_active=True,
                )
            old_assigned = ticket.assigned_to_id
            ticket.assigned_to = assigned_user
            ticket.save()
            create_audit_log(
                request=request,
                action="ASSIGN_TICKET",
                table_name="support_supportticket",
                record_id=ticket.pk,
                old_value={"assigned_to": old_assigned},
                new_value={
                    "assigned_to": (
                        assigned_user.pk
                        if assigned_user
                        else None
                    ),
                },
            )
            if assigned_user:
                Notification.objects.create(
                    user=assigned_user,
                    notification_type="support_assignment",
                    title="Support Ticket Assigned",
                    message=(
                        f"Ticket {ticket.ticket_number} has been assigned to you."
                    ),
                    reference_type="support_ticket",
                    reference_id=ticket.pk,
                )
            Notification.objects.create(
                user=ticket.user,
                notification_type="support_ticket",
                title="Ticket Assignment Updated",
                message=(
                    f"Support assignment for ticket {ticket.ticket_number} "
                    f"has been updated."
                ),
                reference_type="support_ticket",
                reference_id=ticket.pk,
            )
            messages.success(
                request,
                "Ticket assignment updated successfully.",
            )
            return redirect("ticket_detail", pk=pk)
        if action == "delete_ticket":
            if not request.user.is_superuser and not request.user.has_perm(
                "support.delete_supportticket"
            ):
                raise PermissionDenied
            ticket_number = ticket.ticket_number
            ticket_subject = ticket.subject
            try:
                with transaction.atomic():
                    create_audit_log(
                        request=request,
                        action="DELETE",
                        table_name="support_supportticket",
                        record_id=ticket.pk,
                        old_value={
                            "ticket_number": ticket_number,
                            "subject": ticket_subject,
                            "status": ticket.status,
                            "priority": ticket.priority,
                        },
                    )
                    ticket.delete()
                messages.success(
                    request,
                    f"Ticket {ticket_number} deleted successfully.",
                )
                return redirect("ticket_list")
            except ProtectedError:
                messages.error(
                    request,
                    "This ticket cannot be deleted because it is linked with other records.",
                )
                return redirect("ticket_detail", pk=pk)
    context = {
        "page_title": "Ticket Details",
        "breadcrumb_items": [
            {
                "title": "Ticket Details",
                "url": "ticket_detail", 
            },
        ],
        "ticket": ticket,
        "users": User.objects.filter(
            is_active=True
        ).order_by(
            "first_name",
            "last_name",
            "username",
        ),
        "status_choices": SupportTicket.Status.choices,
        "priority_choices": SupportTicket.Priority.choices,
    }
    return render(
        request,
        "support/ticket_detail.html",
        context,
    )
@login_required
@support_permission("support.view_supportcategory")
def category_list(request):
    categories = SupportCategory.objects.annotate(
        ticket_count=Count("support_tickets")
    ).order_by("name")
    context = {
        "page_title": "Support Categories",
        "breadcrumb_items": [
            {
                "title": "Support Categories",
                "url": "category_list", 
            },
        ],
        "categories": categories,
    }
    return render(
        request,
        "support/category_list.html",
        context,
    )
@login_required
@support_permission("support.add_supportcategory")
def category_form(request, pk=None):
    category = get_object_or_404(
        SupportCategory,
        pk=pk,
    ) if pk else None
    if category and not request.user.is_superuser and not request.user.has_perm(
        "support.change_supportcategory"
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = SupportCategoryForm(
            request.POST,
            instance=category,
        )
        if form.is_valid():
            category = form.save()
            create_audit_log(
                request=request,
                action="UPDATE" if pk else "CREATE",
                table_name="support_supportcategory",
                record_id=category.pk,
                new_value={
                    "name": category.name,
                    "description": category.description,
                    "is_active": category.is_active,
                },
            )
            messages.success(
                request,
                f"Category '{category.name}' "
                f"{'updated' if pk else 'created'} successfully.",
            )
            return redirect("category_list")
    else:
        form = SupportCategoryForm(
            instance=category,
        )
    context = {
        "page_title": "Edit Category" if category else "Add Category",
        "breadcrumb_items": [
            {
                "title": "Categories",
                "url": reverse("category_list"),
            },
            {
                "title": "Edit Category" if category else "Add Category",
                "url": (
                    reverse("category_edit", args=[category.id])
                    if category
                    else reverse("category_add")
                ),
            },
        ],
        "form": form,
        "category": category,
    }
    return render(
        request,
        "support/category_form.html",
        context,
    )
@login_required
@support_permission("support.delete_supportcategory")
def category_delete(request, pk):
    category = get_object_or_404(
        SupportCategory,
        pk=pk,
    )
    if request.method != "POST":
        return redirect("category_list")
    if category.support_tickets.exists():
        messages.error(
            request,
            "This category cannot be deleted because support tickets are using it.",
        )
        return redirect("category_list")
    category_name = category.name
    try:
        with transaction.atomic():
            create_audit_log(
                request=request,
                action="DELETE",
                table_name="support_supportcategory",
                record_id=category.pk,
                old_value={
                    "name": category.name,
                    "description": category.description,
                    "is_active": category.is_active,
                },
            )
            category.delete()
        messages.success(
            request,
            f"Category '{category_name}' deleted successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This category cannot be deleted because it is linked with other records.",
        )
    return redirect("category_list")
@login_required
@support_permission("support.view_notification")
def notification_list(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")
    unread_count = notifications.filter(
        is_read=False
    ).count()
    context = {
        "page_title": "Notifications",
        "breadcrumb_items": [
            {
                "title": "Notifications",
                "url": "notification_list", 
            },
        ],
        "notifications": notifications,
        "unread_count": unread_count,
    }
    return render(
        request,
        "support/notification_list.html",
        context,
    )
@login_required
@support_permission("support.view_notification")
def notification_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    if (
        notification.reference_type == "support_ticket"
        and notification.reference_id
    ):
        return redirect(
            "ticket_detail",
            pk=notification.reference_id,
        )
    if (
        notification.reference_type == "ride_request"
        and notification.reference_id
    ):
        return redirect(
            "ride_request_details",
            pk=notification.reference_id,
        )
    return redirect("notification_list")

@login_required
@support_permission("support.change_notification")
def notification_read_all(request):
    if request.method == "POST":
        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )
        messages.success(
            request,
            "All notifications marked as read.",
        )
    return redirect("notification_list")

@login_required
@support_permission("support.view_notification")
def notification_status(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).count()

    notification_data = []

    for notification in notifications:
        if (
            notification.reference_type == "ride_request"
            and notification.reference_id
        ):
            url = reverse(
                "notification_read",
                args=[notification.pk],
            )
        elif (
            notification.reference_type == "support_ticket"
            and notification.reference_id
        ):
            url = reverse(
                "notification_read",
                args=[notification.pk],
            )
        else:
            url = reverse(
                "notification_read",
                args=[notification.pk],
            )

        notification_data.append({
            "id": notification.pk,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": (
                notification.created_at.strftime(
                    "%d %b %Y, %I:%M %p"
                )
                if notification.created_at
                else ""
            ),
            "url": url,
        })

    return JsonResponse({
        "unread_count": unread_count,
        "notifications": notification_data,
    })