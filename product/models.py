"""
here we have our models of product_app 
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.



# this is our main concept of product :
class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True,blank=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name



# here we have courses of our main concept , it has two types : (online and offline) :
class Course(models.Model):
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name='courses')
    title = models.CharField(max_length=20)
    description = models.TextField(null=True,blank=True)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='courses')
    base_price = models.IntegerField()
    discount_type = models.CharField(
        max_length=10, 
        choices=[
            ('percent', 'درصدی'), 
            ('amount', 'ریالی'), 
            ('none', 'بدون تخفیف')], 
            default='none')
    discount = models.IntegerField(default=0)
    final_price = models.IntegerField(default=0)
    type = models.CharField(
        max_length=20,
        choices=[
        ("online" , "online"),
        ("offline","offline")])
    is_active = models.BooleanField(default=True)    
    # this atrs are for online classes :
    start_date = models.DateTimeField(null=True, blank=True)  
    end_date = models.DateTimeField(null=True, blank=True)  
    registration_deadline = models.DateTimeField(null=True, blank=True)  
    class_link = models.URLField(blank=True)
    # this atr is for offline classes :
    access_days = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title','-final_price','type','is_active']

    def __str__(self):
        return self.title    

    # this func calculate final price of course :
    def save(self, *args, **kwargs):
        if self.discount_type == 'percent':
            self.final_price = self.base_price - (self.base_price * self.discount // 100)
        elif self.discount_type == 'amount':
            self.final_price = self.base_price - self.discount
        else:
            self.final_price = self.base_price
        if self.final_price < 0:
            self.final_price = 0
        super().save(*args, **kwargs)

    # this func check access of courses : 
    def is_available_for_purchase(self):
        if not self.is_active:
            return False        
        if self.type == 'online':
            now = timezone.now()
            if self.registration_deadline and now > self.registration_deadline:
                return False
            return True        
        elif self.type == 'offline':
            return True
        return False

    # this func calculate group price :
    def calculate_group_price(self, participant_count):
        if participant_count >= 5:
            return self.final_price * participant_count * 0.8 
        elif participant_count >= 3:
            return self.final_price * participant_count * 0.9  
        return self.final_price * participant_count



# we have chapters for course (course can have many chapters) :
class Chapter(models.Model):
    course = models.ForeignKey(Course,on_delete=models.PROTECT, related_name='chapters')
    title = models.CharField(max_length=20)
    order = models.IntegerField()

    class Meta:
        ordering = ['title','-order']



# we have videos of chpter :
class Video(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT, related_name='videos')
    title = models.CharField(max_length=20)
    order = models.IntegerField(default=1)
    # file = models.FileField(upload_to='category/course/chapter/video/',null=True,blank=True)
    file = models.FileField(upload_to='videos/')
    duration = models.TimeField()

    class Meta:
        ordering = ['title','-order']



# we have attachments of chpter :
class Attachment(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT, related_name='attachments')
    title = models.CharField(max_length=20)
    order = models.IntegerField(default=1)
    # file = models.FileField(upload_to='category/course/chapter/attachment/',null=True,blank=True)
    file = models.FileField(upload_to='attachments/')

    class Meta:
        ordering = ['title','-order']