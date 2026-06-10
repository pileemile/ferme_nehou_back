from django.core.exceptions import ObjectDoesNotExist

from app.customers.models import CustomerModel


def _derive_customer_names(user):
    email_prefix = (getattr(user, "email", "") or "client").split("@", 1)[0].strip()
    username = (getattr(user, "username", "") or "").strip()
    first_name = (getattr(user, "first_name", "") or "").strip()
    last_name = (getattr(user, "last_name", "") or "").strip()

    return (
        first_name or username or email_prefix or "Client",
        last_name or "Client",
    )


def ensure_customer_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return None

    email = (getattr(user, "email", None) or "").lower().strip()
    if not email:
        return None

    if hasattr(user, "customer_profile") and user.customer_profile is not None:
        customer = user.customer_profile
    else:
        try:
            customer = CustomerModel.objects.get(user=user)
        except ObjectDoesNotExist:
            try:
                customer = CustomerModel.objects.get(email=email)
            except ObjectDoesNotExist:
                first_name, last_name = _derive_customer_names(user)
                customer = CustomerModel.objects.create(
                    user=user,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                return customer

    first_name, last_name = _derive_customer_names(user)
    updated_fields = []

    if customer.user_id != user.id:
        customer.user = user
        updated_fields.append("user")
    if customer.email != email:
        customer.email = email
        updated_fields.append("email")
    if not customer.first_name:
        customer.first_name = first_name
        updated_fields.append("first_name")
    if not customer.last_name:
        customer.last_name = last_name
        updated_fields.append("last_name")

    if updated_fields:
        customer.full_clean()
        customer.save(update_fields=updated_fields)

    return customer


def get_customer_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return None
    return ensure_customer_for_user(user)
