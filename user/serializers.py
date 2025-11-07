from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Register_Step1_Serializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    personal_id = serializers.CharField()
    phone_number = serializers.CharField()

    def validate_personal_id(self, value):
        if User.objects.filter(personal_id=value).exists():
            raise serializers.ValidationError("personal id already used")
        return value

    def create(self, validated_data):
        # ایجاد کاربر غیرفعال موقت تا زمانی که OTP تأیید شود
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            personal_id=validated_data['personal_id'],
            phone_number=validated_data['phone_number'],
            is_active=False
        )
        return user


class Register_Step2_Serializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    phone_number = serializers.CharField()

    def validate(self, data):
        # بررسی مطابقت رمزها
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("passwords do not match")

        # بررسی تکراری نبودن نام کاربری
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("username in use")

        # بررسی اینکه شماره تلفن در مرحله اول ثبت شده باشد
        try:
            user = User.objects.get(phone_number=data['phone_number'], is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError("no pending registration for this phone")

        self.user = user
        return data


    def save(self):
        user = self.user
        user.username = self.validated_data['username']
        user.set_password(self.validated_data['password'])
        user.save()

        # تولید و ارسال OTP برای تأیید شماره
        code = OTP.generate_and_send_for_user(user)
        return user


class Verify_OTP_Serializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("user not found")

        otp = OTP.objects.filter(user=user, used=False).order_by('-created_at').first()
        if not otp:
            raise serializers.ValidationError("no otp found")
        if otp.is_expired():
            raise serializers.ValidationError("otp expired")
        if otp.code != data['code']:
            otp.attempts += 1
            otp.save(update_fields=['attempts'])
            raise serializers.ValidationError("invalid code")

        self.otp = otp
        self.user = user
        return data


    def save(self):
        # علامت زدن OTP به عنوان مصرف‌شده و فعال‌سازی حساب
        self.otp.mark_used()
        self.user.is_active = True
        self.user.is_phone_verified = True
        self.user.save()

        # ارسال پیام خوش‌آمد از طریق Celery
        from .tasks import send_welcome_sms
        send_welcome_sms.delay(self.user.id)

        return self.user
    




class GroupRegisterSerializer(serializers.Serializer):
    users = Register_Step1_Serializer(many=True)

    def create(self, validated_data):
        created_users = []
        for user_data in validated_data['users']:
            serializer = Register_Step1_Serializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            created_users.append(user)
        return created_users
