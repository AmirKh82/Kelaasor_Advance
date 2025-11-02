"""
here we have our models of product_app 
"""
from django.db import models
from django.conf import settings
# Create your models here.


# this is our main concept of product
class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.name


# here we have courses of our main concept : it has two type : online and offline
class Course(models.Model):
    category = models.ForeignKey(to=Category,on_delete=models.PROTECT)
    title = models.CharField(max_length=20)
    description = models.TextField(null=True,blank=True)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    base_price = models.IntegerField()
    discount_type = models.CharField(
        max_length=20,
        choices=[
        ('percent','percent'),
        ('amount' , 'amount')],
        null=True,
        blank=True,
        # default=None
    )
    discount = models.IntegerField(default=0)
    final_price = models.IntegerField(default=0)
    type = models.CharField(
        max_length=20,
        choices=[
        ("online" , "online"),
        ("offline","offline")])
    activate = models.BooleanField()
    # this atrs are for online classes :
    start_date = models.DateTimeField(null=True,blank=True) 
    end_date = models.DateTimeField(null=True,blank=True) 
    class_link = models.URLField(null=True,blank=True)
    # this atr is for offline classes :
    duration_time = models.DurationField(null=True,blank=True)

    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        # if discount is percent :
        if self.discount_type == 'percent':
            self.final_price = self.base_price - (self.base_price * self.discount // 100)
        # if discount is amount :
        elif self.discount_type == 'amount':
            self.final_price = self.base_price - self.discount
        else:
            self.final_price = self.base_price

        if self.final_price < 0:
            self.final_price = 0

        super().save(*args, **kwargs)
    


# we have chapters for course
class Chapter(models.Model):
    course = models.ForeignKey(Course,on_delete=models.PROTECT, related_name='chapters')
    title = models.CharField(max_length=20)
    number = models.IntegerField()


# we have videos of chpter
class Video(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT, related_name='videos')
    title = models.CharField(max_length=20)
    number = models.IntegerField()
    file = models.FileField(upload_to='category/course/chapter/video/',null=True,blank=True)
    duration = models.TimeField()


# we have attachments of chpter
class Attachment(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT, related_name='attachments')
    title = models.CharField(max_length=20)
    number = models.IntegerField()
    file = models.FileField(upload_to='category/course/chapter/attachment/',null=True,blank=True)