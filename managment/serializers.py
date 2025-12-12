"""
managment serializers 
"""
from rest_framework import serializers
from .models import Discount_Code
from common.fields import Flexible_User_Field, Flexible_Course_Field
from django.contrib.auth import get_user_model
from product.models import Course

User = get_user_model()



class Discount_Code_Serializer(serializers.ModelSerializer):
    specific_user = Flexible_User_Field(queryset=User.objects.all(), required=False, allow_null=True)
    specific_course = Flexible_Course_Field(queryset=Course.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Discount_Code
        fields = '__all__'
        read_only_fields = ['usage_count', 'created_at']