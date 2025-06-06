from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import Wallet

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(
            user=instance,
            account_number= instance.phone_number[1:]
        )