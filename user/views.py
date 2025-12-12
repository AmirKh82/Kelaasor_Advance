from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP, Dashboard, Wallet, Basket, Basket_Item, Transaction, Enrollment, Purchased_Course, Ticket, Group_Registration, Group_Members
from .serializers import *
from .permissioms import *
from product.models import Course
from .tasks import send_otp_task, send_ticket_notification



# user first time register step 1 :
class Register_Step1_View(APIView):
    permission_classes = [AllowAny]
    
    # this func send otp for user :
    def post(self, request):
        serializer = Register_Step1_Serializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={'username': f"user_{phone}", 'is_active': False}
            )
            otp = OTP.create_for_user(user)
            send_otp_task.delay(phone, otp.code)
            return Response({'success': True, 'message':'otp sent'})
        return Response({'errors': serializer.errors})



# verfy the code :
class Verify_OTP_View(APIView):
    permission_classes = [AllowAny]
    
    # this func chechs user and code :
    def post(self, request):
        serializer = Verify_OTP_Serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp = serializer.validated_data['otp']
            otp.mark_used()
            user.phone_verified = True
            user.is_active = True
            user.save()
            return Response({'success': True, 'user_id': user.id})
        return Response({'errors': serializer.errors})



# user first time register step 2 
class Register_Step2_View(APIView):
    permission_classes = [IsAuthenticated, Has_Verified_Phone]
    
    # this func checks user complete register :
    def put(self, request):
        user = request.user
        if user.user_data_complete:
            return Response({'message':'data was complete before'})        
        serializer = Register_Step2_Serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
                serializer.save()
                return Response({'success': True})
        return Response({'errors': serializer.errors})



# user dashbord include wallet,ticket,basket,purchasedcourse :
class Dashboard_View(APIView):
    permission_classes = [IsAuthenticated]

    # tihs func check dasbord items :
    def get(self, request):
        dashboard = request.user.dashboard
        wallet = dashboard.wallet
        basket = dashboard.basket
        purchased_courses = Purchased_Course.objects.filter(dashboard=dashboard)   
        transactions = Transaction.objects.filter(dashboard=dashboard)
        tickets = Ticket.objects.filter(dashboard=dashboard)        
        data = {
            'wallet': Wallet_Serializer(wallet).data,
            'basket': Basket_Serializer(basket).data,
            'purchased_courses': Purchased_Course_Serializer(purchased_courses, many=True).data,
            'transactions': Transaction_Serializer(transactions, many=True).data,
            'tickets': Ticket_Serializer(tickets, many=True).data
        }
        return Response(data)



# add course to basket :
class Add_To_Basket_View(APIView):
    permission_classes = [IsAuthenticated, Can_Purchase]
    
    # this func check basket and course :
    def post(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
        except:
            return Response({'error': 'course no found'})
        if not course.is_available_for_purchase():
            return Response({'error': 'couse isnt vailble for buy '})
        if Purchased_Course.objects.filter(dashboard=request.user.dashboard, course=course).exists():
            return Response({'error': 'you have bought this course before'})
        basket = request.user.dashboard.basket
        try:
            basket.add_course(course)
            return Response({'success': True})
        except ValueError as e:
            return Response({'error': str(e)})



# del course from basket :
class Remove_From_Basket_View(APIView):
    permission_classes = [IsAuthenticated, Can_Purchase]
    
    # this func check basket and course :
    def delete(self, request, item_id):
        try:
            item = Basket_Item.objects.get(id=item_id, basket=request.user.dashboard.basket)
            course = item.course
            request.user.dashboard.basket.remove_course(course)
            return Response({'success': True})
        except Basket_Item.DoesNotExist:
            return Response({'error': 'item no found'})



# use discount for course :
class Apply_Discount_View(APIView):
    permission_classes = [IsAuthenticated, Can_Purchase]
    
    # tihs func check corse final price with discount :
    def post(self, request):
        serializer = Apply_Discount_Serializer(data=request.data)
        if serializer.is_valid():
            basket_item_id = serializer.validated_data['basket_item_id']
            code = serializer.validated_data['code']
            try:
                basket_item = Basket_Item.objects.get(id=basket_item_id, basket=request.user.dashboard.basket)
                basket_item.apply_discount(code)
                return Response({'success': True, 'discount_amount': basket_item.discount_amount})
            except Basket_Item.DoesNotExist:
                return Response({'error': 'item no found'})
            except ValueError as e:
                return Response({'error': str(e)})
        return Response({'errors': serializer.errors})



# process :
class Check_out_View(APIView):
    permission_classes = [IsAuthenticated, Can_Purchase]
    
    # this func check dashbord and process :
    def post(self, request):
        user = request.user
        dashboard = user.dashboard
        basket = dashboard.basket
        wallet = dashboard.wallet
        if basket.item_count() == 0:
            return Response({'error': 'basket is free'})
        total = basket.total_amount()
        if wallet.balance < total:
            return Response({'error': 'no enough money'})
        with transaction.atomic():
            try:
                wallet.debit(total)                
                transaction_obj = Transaction.objects.create(
                    dashboard=dashboard,
                    amount=total,
                    transaction_type='purchase',
                    status='completed',
                    payment_code=f"PUR-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                )                
                for item in basket.items.all():
                    access_expires_at = None
                    if item.course.type == 'offline':
                        access_expires_at = timezone.now() + timedelta(days=item.course.access_days)                    
                    Enrollment.objects.create(
                        dashboard=dashboard,
                        course=item.course,
                        access_expires_at=access_expires_at,
                        is_active=True
                    )                    
                    Purchased_Course.objects.create(
                        dashboard=dashboard,
                        course=item.course,
                        is_active=True
                    )
                    transaction_obj.related_course = item.course
                    transaction_obj.save(update_fields=['related_course'])
                basket.clear()                
                return Response({'success': True})
            except Exception as e:
                if 'transaction_obj' in locals():
                    transaction_obj.mark_failed()
                    transaction_obj.refund()
                return Response({'error': 'eror money refund'})



# charge Wallet :
class Wallet_Charge_View(APIView):
    permission_classes = [IsAuthenticated]
    
    # this func check wallet and transaction :
    def post(self, request):
        amount = request.data.get('amount')
        try:
            amount_int = int(amount)
            if amount_int <= 0:
                return Response({'error': 'amount should be positive'})
        except:
            return Response({'error': 'amount is not valid'})
        wallet = request.user.dashboard.wallet
        wallet.credit(amount_int)
        Transaction.objects.create(
            dashboard=request.user.dashboard,
            amount=amount_int,
            transaction_type='deposit',
            status='completed'
        )
        return Response({'success': True, 'new_balance': wallet.balance})



# ticket :
class Create_Ticket_View(APIView):
    permission_classes = [IsAuthenticated]
    
    # this func check ticket process :
    def post(self, request):
        serializer = Ticket_Serializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save(dashboard=request.user.dashboard)
            return Response({'success': True, 'ticket_id': ticket.id})
        return Response({'errors': serializer.errors})



# exit from account :
class Logout_View(APIView):
    permission_classes = [IsAuthenticated]
    
    # this func doing the exit process :
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'success': True})
        except:
            return Response({'error': 'eror in logout'})



# token(login) :
class Custom_Token_Obtain_Pair_View(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.data.get('access'):
            user = User.objects.get(username=request.data['username'])
            response.data['is_admin_user'] = user.role == 'support_team' and user.support_team_type == 'admin'
        return response
    


# Group registeration :
class GroupRegisterView(APIView):
    permission_classes = [IsAuthenticated, Can_Purchase]
    
    # this func check Group registeration process :
    def post(self, request):
        course_id = request.data.get('course_id')
        members_data = request.data.get('members', [])
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'course no found'})
        if not course.is_available_for_purchase():
            return Response({'error': 'course is no availble fo buy'})
        if Purchased_Course.objects.filter(dashboard=request.user.dashboard, course=course).exists():
            return Response({'error': 'you have bought this course'})
        total_participants = len(members_data) + 1
        total_amount = course.calculate_group_price(total_participants)
        with transaction.atomic():
            group_reg = Group_Registration.objects.create(
                main_user=request.user,
                course=course,
                total_participants=total_participants,
                total_amount=total_amount,
                status='pending'
            )
            for member_data in members_data:
                Group_Members.objects.create(
                    group_registration=group_reg,
                    first_name=member_data.get('first_name'),
                    last_name=member_data.get('last_name'),
                    phone_number=member_data.get('phone_number'),
                    national_code=member_data.get('national_code')
                )
            from .tasks import send_group_invitation
            for member in group_reg.members.all():
                send_group_invitation.delay(member.phone_number)
        return Response({'success': True, 'group_id': group_reg.id})



# group member :
class My_Group_Registrations_View(APIView):
    permission_classes = [IsAuthenticated]
    
    # this func chech members :
    def get(self, request):
        groups = Group_Registration.objects.filter(main_user=request.user)
        serializer = Group_Registration_Serializer(groups, many=True)
        return Response({'success': True, 'groups': serializer.data})