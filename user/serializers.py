"""
serializer of models 
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from common.fields import Flexible_User_Field, Flexible_Category_Field, Flexible_Course_Field, Flexible_Chapter_Field
from .models import User, OTP, Dashboard, Wallet, Basket, Basket_Item, Transaction, Enrollment, Ticket,Purchased_Course, Group_Registration, Group_Members
from product.models import Course

User = get_user_model()



# user first time register step 1 :
class Register_Step1_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

    # in this func phone number should be uniqe :
    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("phone_number should have 11 numbers")
        if not value.startswith('09'):
            raise serializers.ValidationError("phone_number should start with 09")
        if User.objects.filter(phone_number=value, is_active=True).exists():
            raise serializers.ValidationError("phone_number was exist")
        return value



# verfy the code :
class Verify_OTP_Serializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

    # this func chechs otps validtions :
    def validate(self, data):
        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("can not found user")
        
        otp = OTP.objects.filter(user=user, used=False).order_by('-created_at').first()
        if not otp:
            raise serializers.ValidationError("otp was not verfied")
        if otp.is_expired():
            raise serializers.ValidationError("otp was was expired")
        if otp.attempts >= 5:
            otp.mark_used()
            raise serializers.ValidationError("more attemps than allowd amount")
        if otp.code != data['code']:
            otp.increment_attempts()
            raise serializers.ValidationError("false oto")
        
        data['user'] = user
        data['otp'] = otp
        return data



# user first time register step 2 :
class Register_Step2_Serializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'personal_id', 'username', 'password', 'password2']

    # this func check validition of users password :
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "no same password"})
        validate_password(data['password'])
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "username is repetitve"})
        return data

    # this func update of users password : 
    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.set_password(password)
        instance.user_data_complete = True
        instance.save()
        return instance



# user serializers :
class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 
                 'role', 'support_team_type', 'phone_verified', 'user_data_complete']



# basket item(part of basket) serializer :
class Basket_Item_Serializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_price = serializers.IntegerField(source='course.final_price', read_only=True)
    final_price = serializers.IntegerField(read_only=True)
    discount_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Basket_Item
        fields = ['id', 'course', 'course_title', 'original_price', 'final_price', 
                 'discount_amount', 'applied_discount_code', 'added_at']



# basket(part of user dashbord) serializer :
class Basket_Serializer(serializers.ModelSerializer):
    items = Basket_Item_Serializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Basket
        fields = ['id', 'items', 'total_amount', 'is_paid']

    # this func checks final price of basket :
    def get_total_amount(self, obj):
        return obj.total_amount()



# ................................................................................
# class Enrollment_Serializer(serializers.ModelSerializer):
#     course_title = serializers.CharField(source='course.title', read_only=True)
#     course_type = serializers.CharField(source='course.type', read_only=True)

#     class Meta:
#         model = Enrollment
#         fields = ['id', 'course', 'course_title', 'course_type', 'enrolled_at', 
#                  'access_expires_at', 'is_active']
# .................................................................................



# purchased course(part of user dashbord) serializer :
class Purchased_Course_Serializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_type = serializers.CharField(source='course.type', read_only=True)
    access_expires_at = serializers.SerializerMethodField()

    class Meta:
        model = Purchased_Course
        fields = ['id', 'course', 'course_title', 'course_type', 'purchased_at', 'access_expires_at', 'is_active']

    # tihs func chechs access of courses by enrollment :
    def get_access_expires_at(self, obj):
        enrollment = Enrollment.objects.filter(dashboard=obj.dashboard, course=obj.course).first()
        return enrollment.access_expires_at if enrollment else None



# transaction(part of user dashbord) serializer :
class Transaction_Serializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='related_course.title', read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'status', 'related_course', 
                 'course_title', 'payment_code', 'created_at']



# ticket(part of user dashbord) serializer :
class Ticket_Serializer(serializers.ModelSerializer):
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    course_title = serializers.CharField(source='related_course.title', read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'message', 'department', 'department_display', 'related_course',
    '              course_title', 'status', 'status_display', 'created_at', 'updated_at']



# wallet(part of dasbord) seria;izer :
class Wallet_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance']



# check dicount serializer :
class Apply_Discount_Serializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    basket_item_id = serializers.IntegerField()



# group members(part of group) serializer :
class Group_Members_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Group_Members
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'national_code', 
                 'is_activated', 'has_paid', 'created_at']



# group registrations erializer :
class Group_Registration_Serializer(serializers.ModelSerializer):
    members = Group_Members_Serializer(many=True, read_only=True)
    course = Flexible_Course_Field(queryset=Course.objects.all())  
    main_user = Flexible_User_Field(queryset=User.objects.all())  
    course_title = serializers.CharField(source='course.title', read_only=True)
    main_user_name = serializers.CharField(source='main_user.get_full_name', read_only=True)

    class Meta:
        model = Group_Registration
        fields = ['id', 'course', 'course_title', 'main_user', 'main_user_name', 
                 'members', 'total_participants', 'total_amount', 'status', 'created_at']