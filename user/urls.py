"""
urls for views of user field
"""
from django.urls import path
from .views import (
    Register_Step1_View, Verify_OTP_View, Register_Step2_View,
    Dashboard_View, Add_To_Basket_View, Remove_From_Basket_View,
    Apply_Discount_View, Check_out_View, Wallet_Charge_View,
    Create_Ticket_View, GroupRegisterView, My_Group_Registrations_View,
    Logout_View, Custom_Token_Obtain_Pair_View
)
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    # register ulr :
    path('register-step1', Register_Step1_View.as_view()),
    path('verify-otp', Verify_OTP_View.as_view()),
    path('registeristep2', Register_Step2_View.as_view()),
    # enter and exit url :
    path('login', Custom_Token_Obtain_Pair_View.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('logout', Logout_View.as_view()),
    # dashbord url :
    path('dashboard', Dashboard_View.as_view()),
    path('add-basket', Add_To_Basket_View.as_view()),
    path('remove-basket/<int:item_id>/', Remove_From_Basket_View.as_view()),
    path('basket/apply-discount', Apply_Discount_View.as_view()),
    path('checkout', Check_out_View.as_view()),
    path('charge-wallet', Wallet_Charge_View.as_view()),
    path('create-ticket', Create_Ticket_View.as_view()),
    # group registers url :
    path('group-register', GroupRegisterView.as_view()),
    path('my-groups', My_Group_Registrations_View.as_view()),
]