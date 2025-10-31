"""
here we have our views of product_app : function of models 
"""
from django.shortcuts import render
from product.serializers import Category_Serializers,Course_Serializers
from product.models import Category,Course
from rest_framework import viewsets
from rest_framework import permissions
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
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

class Course_View_Set(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = Course_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['category','title','type']
    filterset_fields = ['category','title','description','base_price','type']
    ordering_fields = ['base_price','start_date']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]