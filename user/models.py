from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expiry = models.DateTimeField(blank=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user/profile/image', blank=True, null=True,
                              validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    address = models.TextField(blank=True, null=True)
    nin = models.CharField(max_length=11, unique=True)
    bvn = models.CharField(max_length=11, unique=True)
    id_verification_status = models.CharField(max_length=20,
                                              choices=[('pending', 'Pending'),
                                                       ('verified', 'Verified'),
                                                       ('rejected', 'Rejected')],
                                              default='pending')
    address_verification_status = models.CharField(max_length=20,
                                                   choices=[('pending', 'Pending'),
                                                            ('verified', 'Verified'),
                                                            ('rejected', 'Rejected')],
                                                   default='pending')
    id_document = models.FileField(upload_to='user/verification/id', blank=True, null=True,
                                   validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'pdf'])])
    address_document = models.FileField(upload_to='user/verification/address', blank=True, null=True,
                                        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'pdf'])])
