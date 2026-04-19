from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customers", "0003_customermodel_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("info", "Information"),
                            ("success", "Succès"),
                            ("warning", "Avertissement"),
                            ("error", "Erreur"),
                            ("reservation", "Réservation"),
                            ("review", "Avis"),
                            ("payment", "Paiement"),
                        ],
                        default="info",
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("link", models.URLField(blank=True, null=True)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="customers.customermodel",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "is_read"], name="notificatio_user_id_7a9f29_idx"),
                    models.Index(fields=["-created_at"], name="notificatio_created_567552_idx"),
                ],
            },
        ),
    ]
