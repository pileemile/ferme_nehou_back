from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.utils.customers import ensure_customer_for_user

User = get_user_model()


@receiver(post_save, sender=User)
def sync_customer_profile(sender, instance, **kwargs):
    ensure_customer_for_user(instance)
