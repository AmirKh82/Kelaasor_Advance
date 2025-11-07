# user/tasks.py
from celery import shared_task
from django.conf import settings
# integrate with SMS provider (Twilio, Kavenegar, ...)

@shared_task
def send_sms_task(phone_number, message):
    # example pseudocode for Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    # client.messages.create(body=message, from_=settings.TWILIO_FROM, to=phone_number)
    # Or call your local sms gateway API
    print(f"send sms to {phone_number}: {message}")
    return True

@shared_task
def send_welcome_sms(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    # mask password: do NOT store raw password, so instead show username and say "password set" or send partial
    message = f"ثبت‌نام شما با موفقیت انجام شد. نام کاربری: {user.username}."
    send_sms_task.delay(user.phone_number, message)
    return True
