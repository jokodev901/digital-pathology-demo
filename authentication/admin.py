from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Permissions', {'fields': ('is_contributor',)}),
    )
    list_display = UserAdmin.list_display + ('is_contributor',)
    list_filter = UserAdmin.list_filter + ('is_contributor',)
    pass
