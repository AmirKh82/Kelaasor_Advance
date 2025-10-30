"""
here we have our serializers of product_app 
"""
from rest_framework.serializers import ModelSerializer
from product.models import Category


class Category_Serializers(ModelSerializer):
    class Meta :
        model = Category
        fields = '__all__'