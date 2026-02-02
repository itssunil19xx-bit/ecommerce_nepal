from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'avatar',
        'date_of_birth',
        'company_name',
        'pan_vat_number',
        'seller_license',
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role',
                    'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number',
                'province', 'district', 'municipality', 'ward_no'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'is_email_verified', 'is_phone_verified',
                'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    inlines = [UserProfileInline]

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', )
    search_fields = ('user__email', 'user__first_name',
                     'user__last_name', 'company_name')
    list_filter = ('user__role',)
