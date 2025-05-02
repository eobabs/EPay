from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=10, unique=True)


    def deposit(self, amount):
        if amount > Decimal('0.00'):
            self.balance += amount
            self.save()
            return True
        return False

    def withdraw(self, amount):
        if amount > Decimal('0.00'):
            if amount <= self.balance:
                self.balance -= amount
                self.save()
                return True
        return False

class Transaction(models.Model):

    TRANSACTION_TYPE = [
        ("D", "DEPOSIT"),
        ("W", "WITHDRAW"),
        ("T", "TRANSFER"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference =models.CharField(max_length=40, unique=True)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE, default='D')
    transaction_time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender', null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE ,related_name='receiver', null=True)

    def save(self, *args, **kwargs):
        if self.sender is None and self.receiver is None:
            raise ValidationError("Sender and receiver cannot be None")
        super().save(*args, **kwargs)


