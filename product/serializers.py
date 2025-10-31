"""
here we have our serializers of product_app 
"""
from rest_framework import serializers
from .models import Category, Course


class Category_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class FlexibleCategoryField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass


        try:
            return self.get_queryset().get(title=data)
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category with title '{data}' not found.")


class Course_Serializers(serializers.ModelSerializer):
    category = FlexibleCategoryField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
