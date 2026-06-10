# Generated manually to link customer profiles to authenticated users.

from django.conf import settings
from django.db import migrations, models


def link_customers_to_users(apps, schema_editor):
    CustomerModel = apps.get_model("customers", "CustomerModel")
    User = apps.get_model("authentification", "User")

    users_by_email = {
        user.email.strip().lower(): user
        for user in User.objects.exclude(email__isnull=True).exclude(email__exact="")
    }

    for customer in CustomerModel.objects.all():
        email = (customer.email or "").strip().lower()
        user = users_by_email.get(email)
        if user is not None:
            customer.user_id = user.id
            customer.save(update_fields=["user"])


def unlink_customers_from_users(apps, schema_editor):
    CustomerModel = apps.get_model("customers", "CustomerModel")
    CustomerModel.objects.exclude(user__isnull=True).update(user=None)


class Migration(migrations.Migration):

    dependencies = [
        ("authentification", "0001_initial"),
        ("customers", "0002_alter_customermodel_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customermodel",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="customer_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(link_customers_to_users, unlink_customers_from_users),
    ]
