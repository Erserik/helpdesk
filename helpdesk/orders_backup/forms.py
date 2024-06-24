from django import forms
from .models import Order

class OrderProfileForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['building', 'room_number', 'problem_type', 'description', 'document']

class OrderStatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ('accepted', 'Принято'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
        ('freeze', 'Заморожен')
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    comment = forms.CharField(widget=forms.Textarea, required=False)
