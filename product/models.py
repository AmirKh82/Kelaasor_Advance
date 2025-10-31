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
    discount = models.IntegerField()
    final_price = models.IntegerField()
    type = models.CharField(
        max_length=20,
        choices=[
        ("online" , "online"),
        ("offline","offfline")])
    activate = models.BooleanField()
    # this atrs are for online classes :
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    class_link = models.URLField(null=True,blank=True)
    # this atr is for offline classes :
    duration_date = models.TimeField()


# we have chapters for course
class Chapter(models.Model):
    course = models.ForeignKey(Course,on_delete=models.PROTECT)
    title = models.CharField()
    number = models.IntegerField()


# we have videos of chpter
class Video(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT)
    title = models.CharField()
    number = models.IntegerField()
    file = models.FileField(upload_to='category/course/chapter/video/',null=True,blank=True)
    duration = models.TimeField()


# we have attachments of chpter
class Attachment(models.Model):
    chapter = models.ForeignKey(Chapter,on_delete=models.PROTECT)
    title = models.CharField()
    number = models.IntegerField()
    file = models.FileField(upload_to='category/course/chapter/attachment/',null=True,blank=True)