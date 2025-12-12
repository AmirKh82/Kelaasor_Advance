"""
models of our user field
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
# Create your models here.



# base user data :
class User(AbstractUser):
    personal_id = models.CharField(max_length=10,unique=True)
    phone_number = models.CharField(max_length=11,unique=True)
    user_data_complete = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=[
        ('teacher','teacher'),
        ('user','user'),
        ('support_team','support_team')],
        default = 'user'
        )
    support_team_type = models.CharField(
        max_length=20, 
        choices=[
        ('edu', 'educational'),       
        ('finance', 'finance'),          
        ('admin', 'admin'),], 
        null=True, 
        blank=True,
        )
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return  f"name : {self.first_name}-{self.last_name} , personal_id : {self.personal_id} , phone_number : {self.phone_number} , username : {self.username}"
    
    # this func checks users can buy or not :
    def can_purchase(self):
        return self.phone_verified and self.user_data_complete and self.is_active



# otp code for registeration :
class OTP(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    # this func checks otp expired or not :
    def is_expired(self):
        return timezone.now > self.expired_at

    # this func checks otp used or not :
    def mark_used(self):
        self.used = True
        self.save(update_fields=['used'])

    # this func checks otp is valid or not :
    def is_valid(self):
        return (not self.used and not self.is_expired() and self.attempts < 5)

    # this func checks the number of attemps and useage od otp :
    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])
        if self.attempts >= 5:
            self.mark_used()
            OTP.create_for_user(self.user)
    
    # this func creates code :
    @classmethod
    def create_for_user(cls, user):
        cls.objects.filter(user=user, used=False).update(used=True)
        code = f"{random.randint(0, 999999):06d}"
        expired_at = timezone.now() + timedelta(minutes=5)
        return cls.objects.create(user=user, code=code, expired_at=expired_at)
    


# every user has dashbord on his account and its create when user register completely:
class Dashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dashboard")
    created_at = models.DateTimeField(auto_now_add=True)



# wallet is part of dashbord includes balance:
class Wallet(models.Model):
    dashboard = models.OneToOneField(Dashboard, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)

    # this func raise wallets balance :
    def credit(self, amount):
        if amount <= 0:
            raise ValueError('the amount should be positive')
        self.balance += amount
        self.save(update_fields=['balance'])
        return self.balance

    # this func lose wallets balance :
    def debit(self, amount):
        if amount <= 0:
            raise ValueError('the amount should be positive')
        if amount > self.balance:
            raise ValueError("haven't enough amount")
        self.balance -= amount
        self.save(update_fields=['balance'])
        return self.balance
    


# basket is part of dashbord includes courses that user want to buy :
class Basket(models.Model):
    dashboard = models.OneToOneField(Dashboard, on_delete=models.CASCADE, related_name='basket')
    is_paid = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    # this func checks final amount of basket for pay ;
    def total_amount(self):
        total = 0
        for item in self.items.all():
            total += item.calculated_price()  
        return total

    # this func checks number of basket items :
    def item_count(self):
        return self.items.count()

    # this func clear basket after payment :
    def clear(self):
        self.items.all().delete()
        self.is_paid = False
        self.save(update_fields=['is_paid'])

    # this func adds courses to basket :
    def add_course(self, course):
        if self.items.filter(course=course).exists():
            raise ValueError('you have this course on your basket')
        Basket_Item.objects.create(basket=self, course=course)

    # this func remove courses to basket :
    def remove_course(self, course):
        self.items.filter(course=course).delete()
        self.save(update_fields=['updated_at'])
        


# basket item is part of basket which is the same course :
class Basket_Item(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey('product.Course', on_delete=models.PROTECT)
    applied_discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.IntegerField(default=0)
    final_price = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('basket', 'course')

    # this func checks final price of course :
    def calculated_price(self):
        if self.final_price > 0:
            return self.final_price
        return self.course.final_price

    # this func checks courses discount :
    def apply_discount(self, discount_code):
        from managment.models import Discount_Code
        try:
            discount = Discount_Code.objects.get(
                code=discount_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            # checking limits 
            if discount.scope == 'course' and discount.specific_course != self.course:
                raise ValueError('this discount is not for this course')
            if discount.scope == 'user' and discount.specific_user != self.basket.dashboard.user:
                raise ValueError('this discount is not for you')
            if discount.usage_type == 'single' and discount.usage_count >= 1:
                raise ValueError('this discount was used')
            if discount.max_usage and discount.usage_count >= discount.max_usage:
                raise ValueError('limit of useage')
            # checking discount 
            if discount.discount_type == 'percent':
                self.discount_amount = self.course.final_price * discount.value // 100
            else:
                self.discount_amount = discount.value
            self.final_price = max(0, self.course.final_price - self.discount_amount)
            self.applied_discount_code = discount_code
            self.save()
            discount.usage_count += 1
            discount.save(update_fields=['usage_count'])
            return True
        except Discount_Code.DoesNotExist:
            raise ValueError('discount is invalid')



# transaction is part of dashbord includes users payments :
class Transaction(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(
        max_length=20, 
        choices=[
            ('deposit', 'deposit'), 
            ('withdrawal', 'withdrawal'), 
            ('purchase', 'purchase'), 
            ('refund', 'refund')])
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'pending'), 
            ('completed', 'completed'), 
            ('failed', 'failed')], 
            default='pending')
    related_course = models.ForeignKey('product.Course', on_delete=models.SET_NULL, null=True, blank=True)
    payment_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    # this func checks payments complete or not :
    def mark_completed(self):
        self.status = 'completed'
        self.save(update_fields=['status'])

    # this func checks payments failed or not :
    def mark_failed(self):
        self.status = 'failed'
        self.save(update_fields=['status'])

    # this func checks payments failed or not if failed we refuncd the money :
    def refund(self):
        if self.transaction_type == 'purchase' and self.status == 'completed':
            self.dashboard.wallet.credit(self.amount)
            self.transaction_type = 'refund'
            self.save(update_fields=['transaction_type'])



# enrollment is part of dashbord check access of courses :
class Enrollment(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('product.Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    access_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('dashboard', 'course')

    # this func checks access of courses :
    def is_access_valid(self):
        if not self.is_active:
            return False
        if self.access_expires_at:
            return timezone.now() <= self.access_expires_at
        return True
    


# Purchased Course is part of dashbord includes the courses that user buy :
class Purchased_Course(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='purchased_courses')
    course = models.ForeignKey('product.Course', on_delete=models.PROTECT, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('dashboard', 'course')



# ticket is part of dashbord includes user tickets :
class Ticket(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=100)
    message = models.TextField()
    department = models.CharField(
        max_length=20, 
        choices=[
            ('edu', 'edu'), 
            ('finance', 'finance'), 
            ('general', 'general')])
    related_course = models.ForeignKey('product.Course', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('open', 'open'), 
            ('answered', 'answered'), 
            ('closed', 'closed')], 
            default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_department_display()}"



# users can have group registration too :
class Group_Registration(models.Model):
    main_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_registrations')
    course = models.ForeignKey('product.Course', on_delete=models.CASCADE)
    total_participants = models.PositiveIntegerField()
    total_amount = models.IntegerField()
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'pending'), 
            ('paid', 'paid'), 
            ('cancelled', 'cancelled')], 
            default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # this func checks final price of group :
    def calculate_total(self):
        return self.course.calculate_group_price(self.total_participants)



# group members is part of group for register :
class Group_Members(models.Model):
    group_registration = models.ForeignKey(Group_Registration, on_delete=models.CASCADE, related_name='members')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=11)
    personal_id = models.CharField(max_length=10,unique=True)
    is_activated = models.BooleanField(default=False)
    has_paid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f"name : {self.first_name}-{self.last_name} , personal_id : {self.personal_id} , phone_number : {self.phone_number} , username : {self.username}"