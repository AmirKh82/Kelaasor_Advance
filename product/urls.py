"""
here we have our urls of product_app , use router-viewset insted of base url-path
"""
from django.urls import path , include
from product.views import Category_View_Set,Course_View_Set
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'category' , Category_View_Set , basename='category')
router.register(r'course' , Course_View_Set , basename='course')

urlpatterns = [
    path('' , include(router.urls)),
    ]
