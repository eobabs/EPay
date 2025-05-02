from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", 'first_name', 'last_name', 'email', 'phone_number'),
            },
        ),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff')
    list_filter = ('first_name', 'last_name', 'email','phone_number')
    list_display_links =  ['username']
    search_fields = ['username', 'email', 'phone_number']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.append('is_superuser')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and change:
            old_obj = type(obj).objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'address', 'bvn', 'nin')
    list_filter = ('address', 'bvn','nin')
    list_display_links = ['user']
    search_fields = ['nin', 'bvn']
