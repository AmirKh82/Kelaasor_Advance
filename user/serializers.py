from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class FlexibleUserField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except (TypeError, ValueError):
            pass

        try:
            return self.get_queryset().get(username=data)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with username '{data}' not found.")


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
