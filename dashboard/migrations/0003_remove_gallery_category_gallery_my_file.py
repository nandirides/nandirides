from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0002_remove_gallery_my_file"),
    ]
    operations = [
        migrations.RemoveField(
        model_name="gallery",
        name="category",
    ),
        migrations.AddField(
            model_name="gallery",
            name="category",
            field=models.CharField(
                choices=[
                    ("profile", "Profile"),
                    ("vehicle", "Vehicle"),
                    ("ride", "Ride"),
                    ("driver", "Driver"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=20,
            ),
        ),
    ]