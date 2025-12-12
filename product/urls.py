"""
here we have our urls of product_app , use router-viewset insted of base url-path
"""
from django.urls import path , include
from product.views import Category_View_Set,Course_View_Set,Chapter_View_Set,Video_View_Set,Attachment_View_Set
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'category' , Category_View_Set , basename='category')
router.register(r'course' , Course_View_Set , basename='course')
router.register(r'chapter' , Chapter_View_Set , basename='chapter')
router.register(r'video' , Video_View_Set , basename='video')
router.register(r'attachment' , Attachment_View_Set , basename='attachment')



urlpatterns = [
    path('' , include(router.urls)),
    ]
