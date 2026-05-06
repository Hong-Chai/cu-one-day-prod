from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'credits', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'credits']
    search_fields = ['username', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('credits', 'expertise')}),
    )
