from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
class Command(BaseCommand):
    help = "Create and configure NandiRide Support Groups and Permissions"
    GROUP_PERMISSIONS = {
        "Support Viewer": [
            "view_supportticket",
            "view_supportcategory",
            "view_notification",
        ],
        "Support Agent": [
            "view_supportticket",
            "add_supportticket",
            "change_supportticket",
            "view_supportcategory",
            "view_notification",
            "change_notification",
        ],
        "Support Manager": [
            "view_supportticket",
            "add_supportticket",
            "change_supportticket",
            "delete_supportticket",
            "view_supportcategory",
            "add_supportcategory",
            "change_supportcategory",
            "delete_supportcategory",
            "view_notification",
            "change_notification",
        ],
    }
    def handle(self, *args, **options):
        app_labels = {
            "support": [
                "view_supportticket",
                "add_supportticket",
                "change_supportticket",
                "delete_supportticket",
                "view_supportcategory",
                "add_supportcategory",
                "change_supportcategory",
                "delete_supportcategory",
                "view_notification",
                "change_notification",
            ]
        }
        self.stdout.write(self.style.MIGRATE_HEADING("Setting up Support roles..."))
        for group_name, permission_names in self.GROUP_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()
            added_permissions = 0
            for permission_name in permission_names:
                permission = Permission.objects.filter(
                    content_type__app_label="support",
                    codename=permission_name,
                ).first()
                if permission:
                    group.permissions.add(permission)
                    added_permissions += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Permission not found: support.{permission_name}"
                        )
                    )
            group.save()
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created group: {group_name} ({added_permissions} permissions)"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated group: {group_name} ({added_permissions} permissions)"
                    )
                )
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Support roles configured successfully."
            )
        )