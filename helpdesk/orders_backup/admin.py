from django.contrib import admin
from .models import Order, Problem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'building', 'room_number', 'problem_type', 'status', 'urgency','created_at']
    list_filter = ['building', 'status', 'problem_type']
    search_fields = ['description', 'user__username']

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['name']
