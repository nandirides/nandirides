from .models import Notification

def notifications(request):
    if not request.user.is_authenticated:
        return {
            "notifications": [],
            "unread_notifications_count": 0,
        }

    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return {
        "notifications": user_notifications,
        "unread_notifications_count": unread_count,
    }