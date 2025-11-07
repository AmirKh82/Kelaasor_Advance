"""
here we have our serializers of product_app 
"""
from rest_framework import serializers
from .models import Category, Course, Chapter, Video, Attachment
from common.fields import Flexible_User_Field,Flexible_Category_Field,Flexible_Course_Field,Flexible_Chapter_Field
from django.contrib.auth import get_user_model


# course serializers (just) for category_seriakizers :
class Category_Course_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['id','title','type','final_price','activate']
        read_only_fields = fields


# category serializers :
class Category_Serializers(serializers.ModelSerializer):
    courses = Category_Course_Serializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'courses']


# video serializers :
class Video_Serializers(serializers.ModelSerializer):
    chapter = Flexible_Chapter_Field(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Video
        fields = '__all__'


# attachment serializers :
class Attachment_Serializers(serializers.ModelSerializer):
    chapter = Flexible_Chapter_Field(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Attachment
        fields = '__all__'


# chapter serializers :
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

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['final_price']


    # this function shows teachers names :
    def get_teachers_names(self, obj):
        return [t.username for t in obj.teachers.all()]
    

    # this function shows discount :
    def get_discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount}% off"
        elif obj.discount_type == 'amount':
            return f"{obj.discount:,} Rial off"
        return "No discount"


    # this function check validtion for course :
    def validate(self, data):
        """
        Validate logic for online/offline course types:
        - Online: must have start_date and end_date
        - Offline: must have duration_time, and should NOT have start/end dates
        """

        course_type = data.get('type') or getattr(self.instance, 'type', None)

        if course_type == "online":
            start_date = data.get('start_date') or getattr(self.instance, 'start_date', None)
            end_date = data.get('end_date') or getattr(self.instance, 'end_date', None)
            if not start_date or not end_date:
                raise serializers.ValidationError("Online courses must have start_date and end_date.")
        elif course_type == "offline":
            duration_time = data.get('duration_time') or getattr(self.instance, 'duration_time', None)
            if not duration_time:
                raise serializers.ValidationError("Offline courses must have duration_time.")
            if data.get('start_date') or data.get('end_date'):
                raise serializers.ValidationError("Offline courses cannot have start_date or end_date.")
        return data