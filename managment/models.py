"""
models of managment and support team
"""
from django.db import models
from django.conf import settings
from product.models import Course



# discount :
class Discount_Code(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10, 
        choices=[
            ('percent', 'percent'), 
            ('amount', 'amount')])
    value = models.IntegerField()
    usage_type = models.CharField(
        max_length=10, 
        choices=[
            ('single', 'single '), 
            ('multiple', 'multiple ')])
    scope = models.CharField(
        max_length=10, 
        choices=[
            ('general', 'general'), 
            ('user', 'user'), 
            ('course', 'course')], 
            default='general')
    specific_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    specific_course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_count = models.IntegerField(default=0)  
    max_usage = models.IntegerField(null=True, blank=True)  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    # this func check discounts validation :
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_to and
                (self.max_usage is None or self.usage_count < self.max_usage))