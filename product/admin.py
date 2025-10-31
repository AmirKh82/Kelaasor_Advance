"""
here we are Personalizing admin panel based on models for the admin 
"""
from django.contrib import admin
from product.models import Category
# Register your models here.


class Category_Admin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name','description']
    list_filter = ['name']


admin.site.register(Category,Category_Admin)