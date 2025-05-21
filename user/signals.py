from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import send_verification_email


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_user_verification(sender, instance, created, **kwargs):
    if created:
        try:
            send_verification_email(instance)
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")