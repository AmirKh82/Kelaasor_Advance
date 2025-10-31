"""
here we are Personalizing admin panel based on models for the admin 
"""
from django.contrib import admin
from product.models import Category , Course
# Register your models here.


class Category_Admin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name','description']
    list_filter = ['name']

class Course_Admin(admin.ModelAdmin):
    list_display = ['category__name','title','show_teachers','base_price','type','start_date','end_date','duration']
    search_fields = ['category__name','title','description','type']
    list_filter = ['category__name','title','description','base_price','type']

    def show_teachers(self, obj):
        return ", ".join([teacher.username for teacher in obj.teachers.all()])
    show_teachers.short_description = "teachers"


admin.site.register(Category,Category_Admin)
admin.site.register(Course,Course_Admin)