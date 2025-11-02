"""
here we are Personalizing admin panel based on models for the admin 
"""
from django.contrib import admin
from product.models import Category , Course, Chapter, Video, Attachment
# Register your models here.


class Category_Admin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name','description']
    list_filter = ['name']

class Course_Admin(admin.ModelAdmin):
    list_display = ['category__name','title','show_teachers','base_price','type','start_date','end_date','duration_time']
    search_fields = ['category__name','title','description','type']
    list_filter = ['category__name','title','description','base_price','type']
    #?
    def show_teachers(self, obj):
        return ", ".join([teacher.username for teacher in obj.teachers.all()])
    show_teachers.short_description = "teachers"


class Chapter_Admin(admin.ModelAdmin):
    list_display = ['course__title','title','number']
    search_fields = ['course__title','title','number']
    list_filter = ['course__title','title','number']

class Video_Admin(admin.ModelAdmin):
    list_display = ['chapter__title','title','number']
    search_fields = ['chapter__title','title','number']
    list_filter = ['chapter__title','title','number']

class Attachment_Admin(admin.ModelAdmin):
    list_display = ['chapter__title','title','number']
    search_fields = ['chapter__title','title','number']
    list_filter = ['chapter__title','title','number']


admin.site.register(Category,Category_Admin)
admin.site.register(Course,Course_Admin)
admin.site.register(Chapter,Chapter_Admin)
admin.site.register(Video,Video_Admin)
admin.site.register(Attachment,Attachment_Admin)