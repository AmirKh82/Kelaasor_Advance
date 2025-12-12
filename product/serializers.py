"""
here we have our serializers of product_app 
"""
from rest_framework import serializers
from .models import Category, Course, Chapter, Video, Attachment
from common.fields import Flexible_User_Field,Flexible_Category_Field,Flexible_Course_Field,Flexible_Chapter_Field
from django.contrib.auth import get_user_model



# course serializers (just) for category_serializers :
class Category_Course_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id','title','type','final_price','is_active']
        read_only_fields = fields



# category serializers :
class Category_Serializers(serializers.ModelSerializer):
    courses = Category_Course_Serializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'courses']



# video(part of chater) serializers :
class Video_Serializers(serializers.ModelSerializer):
    chapter = Flexible_Chapter_Field(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Video
        fields = '__all__'



# attachment(part of chapter) serializers :
class Attachment_Serializers(serializers.ModelSerializer):
    chapter = Flexible_Chapter_Field(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Attachment
        fields = '__all__'



# chapter(part of course) serializers :
class Chapter_Serializers(serializers.ModelSerializer):
    course = Flexible_Course_Field(queryset=Course.objects.all())
    course_title = serializers.CharField(source='course.title', read_only=True)
    videos = Video_Serializers(many=True, read_only=True)
    attachments = Attachment_Serializers(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'



# course serializers :
class Course_Serializers(serializers.ModelSerializer):
    category = Flexible_Category_Field(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    teachers = Flexible_User_Field(queryset=get_user_model().objects.all(), many=True)
    teachers_names = serializers.SerializerMethodField(read_only=True)
    chapters = Chapter_Serializers(many=True, read_only=True)
    discount_display = serializers.SerializerMethodField(read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['final_price']

    # this check teacher name(id) fir course :
    def get_teachers_names(self, obj):
        return [t.username for t in obj.teachers.all()]
    
    # this func check discount :
    def get_discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount}% off"
        elif obj.discount_type == 'amount':
            return f"{obj.discount:,} Rial off"
        return "No discount"
    
    # this func check course for buy that is availbe or not :
    def get_is_available(self, obj):
        return obj.is_available_for_purchase()

    # this func check validition(limit) of course :
    def validate(self, data):
        course_type = data.get('type') or getattr(self.instance, 'type', None)
        if course_type == "online":
            start_date = data.get('start_date') or getattr(self.instance, 'start_date', None)
            end_date = data.get('end_date') or getattr(self.instance, 'end_date', None)
            if not start_date or not end_date:
                raise serializers.ValidationError("Online courses must have start_date and end_date.")
        elif course_type == "offline":
            access_days = data.get('access_days') or getattr(self.instance, 'access_days', None)
            if not access_days:
                raise serializers.ValidationError("Offline courses must have access_days.")
        return data