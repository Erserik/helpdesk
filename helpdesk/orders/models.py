from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


User = get_user_model()
class Problem(models.Model):
    DEPARTMENT_CHOICES = [
        ('AHD', 'AHD'),
        ('DIT', 'DIT'),
    ]

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    BUILDING_CHOICES = [
        ('main', _('Главный')),
        ('baizak', _('Байзак')),
        ('gym', _('Спортзал')),
    ]

    STATUS_CHOICES = [
        ('submitted', _('Отправлено')),
        ('accepted', _('Принято')),
        ('in_progress', _('В процессе')),
        ('completed', _('Завершено')),
        ('freeze', _('Заморожен')),
    ]

    URGENCY_CHOICES = [
        ('urgent', _('Срочно')),
        ('not_urgent', _('Не срочно')),
        ('very_urgent', _('Очень срочно')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    building = models.CharField(max_length=100, choices=BUILDING_CHOICES)
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    room_number = models.CharField(max_length=10)
    problem_type = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='not_urgent')
    document = models.FileField(upload_to='orders/documents/', null=True, blank=True)  # File field added
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.status == 'completed' and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)


    def add_comment_and_update_status(self, user, comment):
        if user.role in ['ahd', 'dit']:
            self.comments = comment
            self.status = 'freeze'
            self.save()

    def __str__(self):
        return f"{self.user}'s order in {self.building} room {self.room_number}"

class ChatMessage(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}'
