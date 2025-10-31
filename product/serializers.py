"""
here we have our serializers of product_app 
"""
from rest_framework import serializers
from .models import Category, Course, Chapter, Video, Attachment


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
            raise serializers.ValidationError(f"Category with name '{data}' not found.")


class FlexibleCourseField(serializers.PrimaryKeyRelatedField):
    """
    admin can work with both id or name
    """
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        try:
            return self.get_queryset().get(title=data)
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with title '{data}' not found.")


class FlexibleChapterField(serializers.PrimaryKeyRelatedField):
    """
    admin can work with both id or name
    """
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        try:
            return self.get_queryset().get(title=data)
        except Chapter.DoesNotExist:
            raise serializers.ValidationError(f"Chapter with title '{data}' not found.")


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
    videos = Video_Serializers(source='video_set', many=True, read_only=True)
    attachments = Attachment_Serializers(source='attachment_set', many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'


class Course_Serializers(serializers.ModelSerializer):
    category = FlexibleCategoryField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    chapters = Chapter_Serializers(source='chapter_set', many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'