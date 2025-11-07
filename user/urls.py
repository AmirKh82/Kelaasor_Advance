from django.urls import path
from .views import RegisterStep1View, RegisterStep2View, VerifyOTPView, GroupRegisterView

urlpatterns = [
    path('register/step1/', RegisterStep1View.as_view()),
    path('register/step2/', RegisterStep2View.as_view()),
    path('register/verify/', VerifyOTPView.as_view()),
    path('register/group/', GroupRegisterView.as_view()),
]
