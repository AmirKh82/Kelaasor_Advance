from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import Register_Step1_Serializer, Register_Step2_Serializer, Verify_OTP_Serializer,GroupRegisterSerializer

# Create your views here.

class RegisterStep1View(APIView):
    def post(self, request):
        s = Register_Step1_Serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"detail":"ok","phone_number":user.phone_number}, status=status.HTTP_201_CREATED)

class RegisterStep2View(APIView):
    def post(self, request):
        s = Register_Step2_Serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"detail":"otp_sent"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    def post(self, request):
        s = Verify_OTP_Serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"detail":"verified"}, status=status.HTTP_200_OK)
    

class GroupRegisterView(generics.CreateAPIView):
    serializer_class = GroupRegisterSerializer
