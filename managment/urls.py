"""
here we have our urls of managment_app , use router-viewset insted of base url-path
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, DiscountCodeViewSet, CourseManagementViewSet



router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'discount-codes', DiscountCodeViewSet, basename='discount-code')
router.register(r'courses', CourseManagementViewSet, basename='course-management')



urlpatterns = [
    path('', include(router.urls)),
]