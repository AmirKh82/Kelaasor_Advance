from rest_framework import serializers
from product.models import Category, Course, Chapter
from django.contrib.auth import get_user_model

User = get_user_model()



class Flexible_Category_Field(serializers.PrimaryKeyRelatedField):
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


class Flexible_Course_Field(serializers.PrimaryKeyRelatedField):
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


class Flexible_Chapter_Field(serializers.PrimaryKeyRelatedField):
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
        

class Flexible_User_Field(serializers.PrimaryKeyRelatedField):
    """
    Allows using both id or username for User relationships.
    Example:
        "teachers": [1, "ali", "maryam"]
    """
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            if str(data).isdigit():
                return queryset.get(id=data)
            return queryset.get(username=data)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User '{data}' not found.")

