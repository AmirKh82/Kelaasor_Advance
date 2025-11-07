"""
here we have our views of product_app : function of models 
"""
from django.shortcuts import render
from product.serializers import Category_Serializers,Course_Serializers,Chapter_Serializers,Video_Serializers,Attachment_Serializers
from product.models import Category,Course,Chapter,Video,Attachment
from rest_framework import viewsets,permissions,filters
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.


# view for category :
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
    
    
# view for course :
class Course_View_Set(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = Course_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['category__name','title','type']
    filterset_fields = ['category__name','title','description','base_price','type']
    ordering_fields = ['base_price','start_date']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

# view for chapter :
class Chapter_View_Set(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = Chapter_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['course__title','title','number']
    filterset_fields = ['course__title','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

# view for video :
class Video_View_Set(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = Video_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['chapter__title','chapter__number','title','number']
    filterset_fields = ['chapter__title','chapter__number','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

# view for attachment :
class Attachment_View_Set(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = Attachment_Serializers
    filter_backends = [filters.SearchFilter , DjangoFilterBackend , filters.OrderingFilter]
    search_fields = ['chapter__title','chapter__number','title','number']
    filterset_fields = ['chapter__title','chapter__number','title','number']
    ordering_fields = ['number']

    def get_permissions(self):
        if self.request.method in ['POST','PATCH','PUT','DELETE']:
           return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]