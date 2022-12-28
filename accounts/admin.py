from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm


UserAdmin.fieldsets[2][1]['fields'] = (         # Customize UserAdmin fields
    "is_active",
    "is_staff",
    "is_superuser",
    "is_author",
    "special_user",
    "groups",
    "user_permissions",
)
UserAdmin.fieldsets[1][1]['fields'] = (          # Customize UserAdmin fields
    "first_name",
    "last_name",
    "email",
    "phone",
    "mobile",
    "home_address",
    "postal_code",
    "age",
    "gender",
    "degree",
)


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name',
                    'email', 'is_author', 'is_special_user','age','gender']
    list_filter = ['username', 'email', 'is_author', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone','postal_code','mobile']
    ordering = ['-date_joined', 'is_author']

# Register your models here.

admin.site.register(CustomUser, CustomUserAdmin)
