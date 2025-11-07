from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
from .tasks import send_sms_task
# Create your models here.


class User(AbstractUser):
    personal_id = models.CharField(max_length=10,nique=True)
    phone_number = models.CharField(max_length=12)

    # class Meta:
    #     ordering = ['username']

    def __str__(self):
        return self.first_name + self.last_name + self.personal_id





class OTP(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=['used'])


    @staticmethod
    def create_otp_for_user(user, expiry_minutes=5):
        code = f"{random.randint(0, 999999):06d}"
        now = timezone.now()
        otp = OTP.objects.create(
            user=user,
            code=code,
            created_at=now,
            expires_at=now + timedelta(minutes=expiry_minutes),
            used=False
        )
        # enqueue sms sending
        send_sms_task.delay(user.phone_number, f"Your verification code: {code}")
        return otp

    @staticmethod
    def generate_and_send_for_user(user, expiry_minutes=5):
        # delete old unused otps or mark them used if you want
        return OTP.create_otp_for_user(user, expiry_minutes=expiry_minutes)