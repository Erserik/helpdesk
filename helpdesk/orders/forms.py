from django import forms

from accounts.models import CustomUser
from .models import Order, ChatMessage, Problem


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


from django import forms


class OrderReassignmentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['executor']
        labels = {
            'executor': 'Исполнитель',
        }

    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order', None)
        super(OrderReassignmentForm, self).__init__(*args, **kwargs)

        # Set the queryset for 'executor' based on the problem type's department
        if order and order.problem_type:
            # Fetch department from problem type and filter users accordingly
            department = order.problem_type.department
            self.fields['executor'].queryset = CustomUser.objects.filter(role__iexact=department)
        else:
            # If no order or problem type, provide an empty queryset
            self.fields['executor'].queryset = CustomUser.objects.none()


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2}),
        }


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['name']

