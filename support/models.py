from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class SupportCategory(TimeStampedModel):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )


class SupportTicket(TimeStampedModel):

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    ticket_number = models.CharField(
        max_length=50,
        unique=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="support_tickets",
    )

    ride = models.ForeignKey(
        "rides.Ride",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="support_tickets",
    )

    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.PROTECT,
    )

    subject = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_support_tickets",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )


class Notification(TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=50,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    reference_type = models.CharField(
        max_length=50,
        blank=True,
    )

    reference_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["user", "is_read"]
            )
        ]

class AuditLog(TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=50,
    )

    table_name = models.CharField(
        max_length=100,
    )

    record_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    old_value = models.JSONField(
        null=True,
        blank=True,
    )

    new_value = models.JSONField(
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

