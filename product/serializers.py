"""
here we have our serializers of product_app 
"""
from rest_framework import serializers
from .models import Category, Course, Chapter, Video, Attachment
from user.serializers import FlexibleUserField, UserShortSerializer
from django.contrib.auth import get_user_model



class Category_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class FlexibleCategoryField(serializers.PrimaryKeyRelatedField):
    """
    admin can work with both id or name    
    """
    def to_internal_value(self, data):
        # (id)
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        # (name)
        try:
            return self.get_queryset().get(name=data)
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category '{data}' not found.")


class FlexibleCourseField(serializers.PrimaryKeyRelatedField):
    """
    admin can work with both id or name
    """
    def to_internal_value(self, data):
        # (id)
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        # (name)
        try:
            return self.get_queryset().get(title=data)
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course '{data}' not found.")


class FlexibleChapterField(serializers.PrimaryKeyRelatedField):
    """
    admin can work with both id or name
    """
    def to_internal_value(self, data):
        # (id)
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        # (name)
        try:
            return self.get_queryset().get(title=data)
        except Chapter.DoesNotExist:
            raise serializers.ValidationError(f"Chapter '{data}' not found.")


class Video_Serializers(serializers.ModelSerializer):
    chapter = FlexibleChapterField(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Video
        fields = '__all__'


class Attachment_Serializers(serializers.ModelSerializer):
    chapter = FlexibleChapterField(queryset=Chapter.objects.all())
    chapter_name = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Attachment
        fields = '__all__'


class Chapter_Serializers(serializers.ModelSerializer):
    course = FlexibleCourseField(queryset=Course.objects.all())
    course_title = serializers.CharField(source='course.title', read_only=True)
    videos = Video_Serializers(many=True, read_only=True)
    attachments = Attachment_Serializers(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'


class Course_Serializers(serializers.ModelSerializer):
    category = FlexibleCategoryField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    teachers = FlexibleUserField(queryset=get_user_model().objects.all(), many=True)
    teachers_names = serializers.SerializerMethodField(read_only=True)
    chapters = Chapter_Serializers(many=True, read_only=True)
    discount_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['final_price']

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
    


    def get_discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount}% off"
        elif obj.discount_type == 'amount':
            return f"{obj.discount:,} Rial off"
        return "No discount"
    

    def get_teachers_names(self, obj):
        return [t.username for t in obj.teachers.all()]