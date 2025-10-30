"""
here we have our views of product_app : function of models 
"""
from django.shortcuts import render
from product.serializers import Category_Serializers
from product.models import Category
from rest_framework import viewsets
from rest_framework import permissions
# from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
# Create your views here.


class Category_View_Set(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = Category_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name','description']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH', 'PUT', 'DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    # def get_renderers(self):
    #     """نمایش فقط JSON برای کاربران غیر ادمین"""
    #     if not self.request.user.is_staff:
    #         return [JSONRenderer()]
    #     return [BrowsableAPIRenderer(), JSONRenderer()]