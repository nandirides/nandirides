from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class AppSetting(TimeStampedModel):
    key = models.CharField(
        max_length=100,
        unique=True
    )

    value = models.TextField()

    description = models.TextField(
        blank=True
    )

    data_type = models.CharField(
        max_length=20,
        default="string"
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.key