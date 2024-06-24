from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('sender', 'Отправитель'),
        ('ahd', 'АХД'),
        ('dit', 'ДИТ'),
        ('head', 'HEAD'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='sender')

    def __str__(self):
        return self.username
