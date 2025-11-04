"""
here we are Customizing admin panel based on models for the admin 
"""
from django.contrib import admin
from product.models import Category , Course, Chapter, Video, Attachment
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.contrib.auth import get_user_model
# Register your models here.

User = get_user_model()


class Category_Admin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name','description']
    list_filter = ['name']
    ordering = ['name']

class Course_Admin(admin.ModelAdmin):
    list_display = ['category__name','title','show_teachers','final_price','type','activate','start_date','end_date','duration_time']
    search_fields = ['category__name','title','description','type','activate','start_date']
    list_filter = [('category', RelatedOnlyFieldListFilter),'title','description','final_price','type', 'activate','start_date']
    ordering = ['title','-final_price','activate']
    # autocomplete_fields = ['teachers']
    filter_horizontal = ('teachers',)

    
    def show_teachers(self, obj):
        return ", ".join([t.username for t in obj.teachers.all()])
    show_teachers.short_description = "Teachers"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('teachers')


class Chapter_Admin(admin.ModelAdmin):
    list_display = ['course__title','title','number']
    search_fields = ['course__title','title','number']
    list_filter = [('course', RelatedOnlyFieldListFilter),'title','number']
    ordering = ['title','-number']

class Video_Admin(admin.ModelAdmin):
    list_display = ['chapter__title','title','number']
    search_fields = ['chapter__title','title','number']
    list_filter = [('chapter', RelatedOnlyFieldListFilter),'title','number']
    ordering = ['title','-number']

class Attachment_Admin(admin.ModelAdmin):
    list_display = ['chapter__title','title','number']
    search_fields = ['chapter__title','title','number']
    list_filter = [('chapter', RelatedOnlyFieldListFilter),'title','number']
    ordering = ['title','-number']


admin.site.register(Category,Category_Admin)
admin.site.register(Course,Course_Admin)
admin.site.register(Chapter,Chapter_Admin)
admin.site.register(Video,Video_Admin)
admin.site.register(Attachment,Attachment_Admin)