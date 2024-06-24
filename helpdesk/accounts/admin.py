from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Define the fields to be displayed in the list view
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    # Define the fields to be used for searching
    search_fields = ('username', 'email', 'role')

    # Add the role field to the fieldsets for user editing
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('role',)}),  # Add the role field here
    )

    # Add the role field to the fieldsets for user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
