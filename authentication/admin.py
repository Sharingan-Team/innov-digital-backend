from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserFace

class UserFaceInline(admin.StackedInline):
    model = UserFace
    fk_name = 'user'
    readonly_fields = ['uploaded_at']
    extra = 0

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [UserFaceInline]

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Statut', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Vérification', {'fields': ('email_verified', 'face_verified')}),
        ('Email Confirmation', {'fields': ('email_code', 'email_code_expires')}),
        ('Dates importantes', {'fields': ('last_login', 'created_at')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'is_staff', 'is_superuser'
            ),
        }),
    )
    readonly_fields = ('created_at', 'last_login')
    list_display = (
        'username', 'email', 'is_staff', 'is_active',
        'email_verified', 'face_verified', 'email_code_expires'
    )
    search_fields = ('username', 'email')
    ordering = ('email',)
