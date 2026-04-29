from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=200, verbose_name="Hanh dong")),
                ("target_type", models.CharField(blank=True, max_length=100, verbose_name="Loai doi tuong")),
                ("target_id", models.CharField(blank=True, max_length=64, verbose_name="ID doi tuong")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="Du lieu bo sung")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Thoi gian")),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Nguoi thuc hien",
                    ),
                ),
            ],
            options={
                "verbose_name": "Nhat ky kiem toan",
                "verbose_name_plural": "Nhat ky kiem toan",
                "ordering": ["-created_at"],
            },
        ),
    ]
