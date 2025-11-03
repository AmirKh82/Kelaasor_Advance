# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class FlexibleUserField(serializers.PrimaryKeyRelatedField):
#     def to_internal_value(self, data):
#         try:
#             return super().to_internal_value(data)
#         except (TypeError, ValueError):
#             pass

#         try:
#             return self.get_queryset().get(username=data)
#         except User.DoesNotExist:
#             raise serializers.ValidationError(f"User with username '{data}' not found.")


# class UserShortSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name']






# common/fields.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class FlexibleUserField(serializers.PrimaryKeyRelatedField):
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
