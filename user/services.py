import random
import string
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

import user


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email):
    otp = generate_verification_code()
    user.verification_code = otp
    user.verification_code_expiry = datetime.now() + timedelta(minutes=10)
    user.save()

    subject = 'Verify your email'
    message = f"""Welcome to Wallet System!
    
    Your verification code is: {otp}
    
    This code will expire in 10 minutes.
    
    Thank you for choosing Wallet System.
    """
    from_email = settings.EMAIL_HOST_USER
    recipient_email = user.email

    send_mail(
        subject=subject,
        recipient_list=[recipient_email],
        message=message,
        from_email=from_email
    )
    return True

def check_verification_code(user, code):
    if user.verification_code != code:
        return False

    if user.verification_code_expiry < datetime.now():
        return False

    user.is_verified = True
    user.verification_code = None
    user.verification_code_expiry = None
    user.save()
    return True