"""
here we have our views of product_app : function of models 
"""
from django.shortcuts import render
from product.serializers import Category_Serializers,Course_Serializers,Chapter_Serializers,Video_Serializers,Attachment_Serializers
from product.models import Category,Course,Chapter,Video,Attachment
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
    

class Chapter_View_Set(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = Chapter_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['course','title','number']
    filterset_fields = ['course','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

class Video_View_Set(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = Video_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['chapter','title','number']
    filterset_fields = ['chapter','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

class Attachment_View_Set(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = Attachment_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['chapter','title','number']
    filterset_fields = ['chapter','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]