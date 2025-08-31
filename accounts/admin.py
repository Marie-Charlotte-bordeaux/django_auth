from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .models import Document

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'is_active', 'is_staff', 'email_verified', 'failed_login_attempts', 'account_locked_until')
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Sécurité'), {'fields': ('failed_login_attempts', 'last_failed_login_at', 'account_locked_until', 'last_password_change', 'email_verified')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    # supprimer username
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title','owner','is_public','created_at')
    search_fields = ('title','content','owner__email')