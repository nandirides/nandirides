from django.contrib.auth import get_user_model
from support.models import Notification

User = get_user_model()


NOTIFICATION_TYPES = {
    "ride_request_created": "ride_request",
    "ride_request_expired": "ride_request",
    "ride_request_cancelled": "ride_request",
    "payment_completed": "payment",
    "payment_failed": "payment",
    "refund_created": "payment",
    "refund_processed": "payment",
    "refund_failed": "payment",
    "ride_created": "ride",
    "ride_booked": "ride",
    "ride_cancelled": "ride",
    "driver_assigned": "ride",
    "driver_accepted": "ride",
    "driver_arriving": "ride",
    "driver_arrived": "ride",
    "ride_started": "ride",
    "ride_completed": "ride",
    "support_ticket_created": "support_ticket",
    "support_ticket_updated": "support_ticket",
}


_NOTIFICATION_FIELDS = frozenset(
    field.name
    for field in Notification._meta.get_fields()
)


def _get_active_notification_users(exclude_user=None):
    queryset = User.objects.filter(
        is_active=True
    ).order_by("id")

    if exclude_user is not None:
        exclude_user_id = getattr(
            exclude_user,
            "pk",
            exclude_user,
        )

        if exclude_user_id:
            queryset = queryset.exclude(
                pk=exclude_user_id
            )

    return queryset


def _build_notification_data(
    user,
    title,
    message,
    notification_type="general",
    reference_type=None,
    reference_id=None,
):
    data = {
        "user": user,
        "notification_type": notification_type,
        "title": title,
        "message": message,
    }

    if (
        reference_type is not None
        and "reference_type" in _NOTIFICATION_FIELDS
    ):
        data["reference_type"] = reference_type

    if (
        reference_id is not None
        and "reference_id" in _NOTIFICATION_FIELDS
    ):
        data["reference_id"] = reference_id

    if "is_read" in _NOTIFICATION_FIELDS:
        data["is_read"] = False

    if "read_at" in _NOTIFICATION_FIELDS:
        data["read_at"] = None

    return data


def _notification_already_exists(
    user,
    notification_type,
    reference_type=None,
    reference_id=None,
):
    if not user:
        return False

    filters = {
        "user": user,
        "notification_type": notification_type,
    }

    if "reference_type" in _NOTIFICATION_FIELDS:
        filters["reference_type"] = reference_type

    if "reference_id" in _NOTIFICATION_FIELDS:
        filters["reference_id"] = reference_id

    return Notification.objects.filter(
        **filters
    ).exists()


def create_notification(
    user,
    title,
    message,
    notification_type="general",
    reference_type=None,
    reference_id=None,
):
    if not user or not getattr(
        user,
        "is_active",
        True,
    ):
        return None

    if _notification_already_exists(
        user,
        notification_type,
        reference_type,
        reference_id,
    ):
        return None

    return Notification.objects.create(
        **_build_notification_data(
            user,
            title,
            message,
            notification_type,
            reference_type,
            reference_id,
        )
    )


def create_notifications(
    users,
    title,
    message,
    notification_type="general",
    reference_type=None,
    reference_id=None,
):
    notifications = []
    seen_user_ids = set()

    for user in users:
        if not user or not getattr(
            user,
            "is_active",
            True,
        ):
            continue

        user_id = getattr(
            user,
            "pk",
            None,
        )

        if not user_id or user_id in seen_user_ids:
            continue

        seen_user_ids.add(user_id)

        if _notification_already_exists(
            user,
            notification_type,
            reference_type,
            reference_id,
        ):
            continue

        notifications.append(
            Notification(
                **_build_notification_data(
                    user,
                    title,
                    message,
                    notification_type,
                    reference_type,
                    reference_id,
                )
            )
        )

    if not notifications:
        return 0

    Notification.objects.bulk_create(
        notifications
    )

    return len(notifications)


def notify_user(
    user,
    title,
    message,
    notification_type="general",
    reference_type=None,
    reference_id=None,
):
    return int(
        create_notification(
            user,
            title,
            message,
            notification_type,
            reference_type,
            reference_id,
        )
        is not None
    )


def notify_admins(
    title,
    message,
    notification_type="general",
    reference_type=None,
    reference_id=None,
    exclude_user=None,
):
    users = _get_active_notification_users(
        exclude_user
    ).filter(
        is_staff=True
    )

    return create_notifications(
        users,
        title,
        message,
        notification_type,
        reference_type,
        reference_id,
    )


def _notify_user_and_admins(
    user,
    user_title,
    user_message,
    admin_title,
    admin_message,
    notification_type,
    reference_type,
    reference_id,
    exclude_user=None,
):
    count = notify_user(
        user=user,
        title=user_title,
        message=user_message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
    )

    count += notify_admins(
        title=admin_title,
        message=admin_message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
        exclude_user=(
            exclude_user
            if exclude_user is not None
            else user
        ),
    )

    return count


def _notify_passenger(
    passenger,
    title,
    message,
    notification_type,
    reference_type,
    reference_id,
):
    return notify_user(
        user=passenger,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
    ) if passenger else 0


def _notify_ride(
    ride,
    passenger_title,
    passenger_message,
    notification_type,
    admin_title,
    admin_message,
    actor=None,
):
    if not ride:
        return 0

    ride_number = getattr(
        ride,
        "ride_number",
        ride.pk,
    )

    return _notify_user_and_admins(
        user=getattr(
            ride,
            "passenger",
            None,
        ),
        user_title=passenger_title,
        user_message=passenger_message.format(
            ride_number=ride_number
        ),
        admin_title=admin_title,
        admin_message=admin_message.format(
            ride_number=ride_number
        ),
        notification_type=notification_type,
        reference_type="ride",
        reference_id=ride.pk,
        exclude_user=actor,
    )


def _notify_payment(
    payment,
    user_title,
    user_message,
    admin_title,
    admin_message,
    notification_type,
):
    if not payment:
        return 0

    payment_number = getattr(
        payment,
        "payment_number",
        payment.pk,
    )

    return _notify_user_and_admins(
        user=getattr(
            payment,
            "user",
            None,
        ),
        user_title=user_title,
        user_message=user_message.format(
            payment_number=payment_number
        ),
        admin_title=admin_title,
        admin_message=admin_message.format(
            payment_number=payment_number
        ),
        notification_type=notification_type,
        reference_type="payment",
        reference_id=payment.pk,
    )


def _notify_refund(
    refund,
    user_title,
    user_message,
    admin_title,
    admin_message,
    notification_type,
):
    if not refund:
        return 0

    payment = getattr(
        refund,
        "payment",
        None,
    )

    if not payment:
        return 0

    amount = getattr(
        refund,
        "refund_amount",
        0,
    )

    payment_number = getattr(
        payment,
        "payment_number",
        payment.pk,
    )

    data = {
        "amount": amount,
        "payment_number": payment_number,
    }

    return _notify_user_and_admins(
        user=getattr(
            payment,
            "user",
            None,
        ),
        user_title=user_title,
        user_message=user_message.format(
            **data
        ),
        admin_title=admin_title,
        admin_message=admin_message.format(
            **data
        ),
        notification_type=notification_type,
        reference_type="payment",
        reference_id=payment.pk,
    )


# =========================================================
# RIDE REQUEST
# =========================================================

def notify_ride_request_created(
    ride_request,
    actor=None,
):
    if not ride_request:
        return 0

    number = getattr(
        ride_request,
        "request_number",
        ride_request.pk,
    )

    passenger = getattr(
        ride_request,
        "passenger",
        None,
    )

    return _notify_user_and_admins(
        user=passenger,
        user_title="Ride Request Created",
        user_message=(
            f"Your ride request {number} "
            "has been created successfully."
        ),
        admin_title="New Ride Request",
        admin_message=(
            f"Ride request {number} "
            "has been created."
        ),
        notification_type=NOTIFICATION_TYPES[
            "ride_request_created"
        ],
        reference_type="ride_request",
        reference_id=ride_request.pk,
        exclude_user=actor,
    )


def notify_new_ride_request(
    ride_request,
    actor=None,
):
    return notify_ride_request_created(
        ride_request,
        actor,
    )


def _create_ride_request_notifications(
    ride_request,
    actor=None,
):
    return notify_ride_request_created(
        ride_request,
        actor,
    )


def notify_ride_request_expired(
    ride_request,
    actor=None,
):
    if not ride_request:
        return 0

    number = getattr(
        ride_request,
        "request_number",
        ride_request.pk,
    )

    return _notify_user_and_admins(
        user=getattr(
            ride_request,
            "passenger",
            None,
        ),
        user_title="Ride Request Expired",
        user_message=(
            f"Your ride request {number} "
            "has expired."
        ),
        admin_title="Ride Request Expired",
        admin_message=(
            f"Ride request {number} "
            "has expired."
        ),
        notification_type=NOTIFICATION_TYPES[
            "ride_request_expired"
        ],
        reference_type="ride_request",
        reference_id=ride_request.pk,
        exclude_user=actor,
    )


def notify_ride_request_cancelled(
    ride_request,
    actor=None,
):
    if not ride_request:
        return 0

    number = getattr(
        ride_request,
        "request_number",
        ride_request.pk,
    )

    return _notify_user_and_admins(
        user=getattr(
            ride_request,
            "passenger",
            None,
        ),
        user_title="Ride Request Cancelled",
        user_message=(
            f"Your ride request {number} "
            "has been cancelled."
        ),
        admin_title="Ride Request Cancelled",
        admin_message=(
            f"Ride request {number} "
            "has been cancelled."
        ),
        notification_type=NOTIFICATION_TYPES[
            "ride_request_cancelled"
        ],
        reference_type="ride_request",
        reference_id=ride_request.pk,
        exclude_user=actor,
    )


# =========================================================
# RIDE
# =========================================================

def notify_ride_created(
    ride,
    actor=None,
):
    return _notify_ride(
        ride=ride,
        passenger_title="Ride Booked",
        passenger_message=(
            "Your ride {ride_number} "
            "has been booked successfully."
        ),
        notification_type=NOTIFICATION_TYPES[
            "ride_booked"
        ],
        admin_title="Ride Created",
        admin_message=(
            "Ride {ride_number} "
            "has been created."
        ),
        actor=actor,
    )


def notify_ride_booked(
    ride,
    actor=None,
):
    return _notify_ride(
        ride=ride,
        passenger_title="Ride Booked",
        passenger_message=(
            "Your ride {ride_number} "
            "has been booked successfully."
        ),
        notification_type=NOTIFICATION_TYPES[
            "ride_booked"
        ],
        admin_title="Ride Booked",
        admin_message=(
            "Ride {ride_number} "
            "has been booked."
        ),
        actor=actor,
    )


def notify_driver_assigned(
    ride,
    actor=None,
):
    if not ride:
        return 0

    ride_number = getattr(
        ride,
        "ride_number",
        ride.pk,
    )

    passenger = getattr(
        ride,
        "passenger",
        None,
    )

    driver = getattr(
        ride,
        "driver",
        None,
    )

    notification_type = NOTIFICATION_TYPES[
        "driver_assigned"
    ]

    count = _notify_user_and_admins(
        user=passenger,
        user_title="Driver Assigned",
        user_message=(
            f"A driver has been assigned "
            f"to your ride {ride_number}."
        ),
        admin_title="Driver Assigned",
        admin_message=(
            f"Driver has been assigned "
            f"to ride {ride_number}."
        ),
        notification_type=notification_type,
        reference_type="ride",
        reference_id=ride.pk,
        exclude_user=actor,
    )

    driver_user = getattr(
        driver,
        "user",
        None,
    ) if driver else None

    if driver_user:
        count += notify_user(
            user=driver_user,
            title="New Ride Assignment",
            message=(
                f"You have been assigned "
                f"to ride {ride_number}."
            ),
            notification_type=notification_type,
            reference_type="ride",
            reference_id=ride.pk,
        )

    return count


def notify_driver_accepted(
    ride,
    actor=None,
):
    return _notify_ride(
        ride=ride,
        passenger_title="Driver Accepted",
        passenger_message=(
            "Your driver has accepted "
            "ride {ride_number}."
        ),
        notification_type=NOTIFICATION_TYPES[
            "driver_accepted"
        ],
        admin_title="Driver Accepted Ride",
        admin_message=(
            "Driver has accepted "
            "ride {ride_number}."
        ),
        actor=actor,
    )


def notify_ride_status_changed(
    ride,
    status,
    actor=None,
):
    if not ride:
        return 0

    status = str(
        status or ""
    ).strip().lower()

    status_config = {
        "driver_arriving": (
            "Driver Arriving",
            "Driver is arriving for your ride.",
            "driver_arriving",
        ),
        "driver_arrived": (
            "Driver Arrived",
            "Your driver has arrived.",
            "driver_arrived",
        ),
        "started": (
            "Ride Started",
            "Your ride has started.",
            "ride_started",
        ),
        "completed": (
            "Ride Completed",
            "Your ride has been completed.",
            "ride_completed",
        ),
        "cancelled": (
            "Ride Cancelled",
            "Your ride has been cancelled.",
            "ride_cancelled",
        ),
    }

    title, message, type_key = status_config.get(
        status,
        (
            "Ride Status Updated",
            f"Ride status changed to {status}.",
            "ride",
        ),
    )

    ride_number = getattr(
        ride,
        "ride_number",
        ride.pk,
    )

    message = (
        f"Ride {ride_number}: {message}"
    )

    return _notify_user_and_admins(
        user=getattr(
            ride,
            "passenger",
            None,
        ),
        user_title=title,
        user_message=message,
        admin_title=title,
        admin_message=message,
        notification_type=type_key,
        reference_type="ride",
        reference_id=ride.pk,
        exclude_user=actor,
    )


# =========================================================
# PAYMENT
# =========================================================

def notify_payment_completed(
    payment,
    actor=None,
):
    return _notify_payment(
        payment=payment,
        user_title="Payment Successful",
        user_message=(
            "Payment {payment_number} "
            "has been completed successfully."
        ),
        admin_title="Payment Completed",
        admin_message=(
            "Payment {payment_number} "
            "has been completed."
        ),
        notification_type=NOTIFICATION_TYPES[
            "payment_completed"
        ],
    )


def notify_payment_failed(
    payment,
    actor=None,
):
    return _notify_payment(
        payment=payment,
        user_title="Payment Failed",
        user_message=(
            "Payment {payment_number} "
            "could not be completed."
        ),
        admin_title="Payment Failed",
        admin_message=(
            "Payment {payment_number} "
            "has failed."
        ),
        notification_type=NOTIFICATION_TYPES[
            "payment_failed"
        ],
    )


# =========================================================
# REFUND
# =========================================================

def notify_refund_created(
    refund,
):
    return _notify_refund(
        refund=refund,
        user_title="Refund Created",
        user_message=(
            "Refund of ₹{amount} for payment "
            "{payment_number} has been created."
        ),
        admin_title="Refund Created",
        admin_message=(
            "Refund of ₹{amount} for payment "
            "{payment_number} has been created."
        ),
        notification_type=NOTIFICATION_TYPES[
            "refund_created"
        ],
    )


def notify_refund_processed(
    refund,
):
    return _notify_refund(
        refund=refund,
        user_title="Refund Completed",
        user_message=(
            "Refund of ₹{amount} for payment "
            "{payment_number} has been processed."
        ),
        admin_title="Refund Completed",
        admin_message=(
            "Refund of ₹{amount} for payment "
            "{payment_number} has been processed."
        ),
        notification_type=NOTIFICATION_TYPES[
            "refund_processed"
        ],
    )


def notify_refund_failed(
    refund,
):
    return _notify_refund(
        refund=refund,
        user_title="Refund Failed",
        user_message=(
            "Refund for payment "
            "{payment_number} "
            "could not be processed."
        ),
        admin_title="Refund Failed",
        admin_message=(
            "Refund for payment "
            "{payment_number} "
            "could not be processed."
        ),
        notification_type=NOTIFICATION_TYPES[
            "refund_failed"
        ],
    )


# =========================================================
# SUPPORT TICKET
# =========================================================

def _notify_support_ticket(
    ticket,
    actor,
    event,
):
    if not ticket:
        return 0

    ticket_id = ticket.pk
    ticket_number = getattr(
        ticket,
        "ticket_number",
        ticket_id,
    )

    config = {
        "created": {
            "admin_title": "New Support Ticket",
            "admin_message": (
                "Support ticket {ticket_number} "
                "has been created."
            ),
            "user_title": "Support Ticket Created",
            "user_message": (
                "Your support ticket {ticket_number} "
                "has been created."
            ),
            "type": "support_ticket_created",
        },
        "updated": {
            "admin_title": "Support Ticket Updated",
            "admin_message": (
                "Support ticket {ticket_number} "
                "has been updated."
            ),
            "user_title": "Support Ticket Updated",
            "user_message": (
                "Your support ticket {ticket_number} "
                "has been updated."
            ),
            "type": "support_ticket_updated",
        },
    }[event]

    return _notify_user_and_admins(
        user=getattr(
            ticket,
            "user",
            None,
        ),
        user_title=config["user_title"],
        user_message=config["user_message"].format(
            ticket_number=ticket_number
        ),
        admin_title=config["admin_title"],
        admin_message=config["admin_message"].format(
            ticket_number=ticket_number
        ),
        notification_type=NOTIFICATION_TYPES[
            config["type"]
        ],
        reference_type="support_ticket",
        reference_id=ticket_id,
        exclude_user=actor,
    )


def notify_support_ticket_created(
    ticket,
    actor=None,
):
    return _notify_support_ticket(
        ticket,
        actor,
        "created",
    )


def notify_support_ticket_updated(
    ticket,
    actor=None,
):
    return _notify_support_ticket(
        ticket,
        actor,
        "updated",
    )