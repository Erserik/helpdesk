from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

class CustomUserManager(UserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Since the USERNAME_FIELD is 'email', we use the email parameter to create the superuser.
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Other fields you want to require during user creation, excluding 'email'
    objects = CustomUserManager()
    ROLE_CHOICES = [
        ('sender', 'Отправитель'),
        ('ahd', 'АХД'),
        ('dit', 'ДИТ'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email  # return self.email since username is not used
