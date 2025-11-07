from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # list_display = ('id', 'username', 'email', 'is_staff', 'is_active')
    # search_fields = ('username', 'email')
    # list_filter = ('is_staff', 'is_superuser', 'is_active')
    pass
