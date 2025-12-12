"""
celery for user field
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import OTP, Ticket, Enrollment
from product.models import Course, Chapter, Video

try:
    from celery import shared_task
except ImportError:
    # برای مواقعی که Celery نصب نیست
    def shared_task(func):
        return func



# send code for phone number :
@shared_task
def send_otp_task(phone_number, code):
    print(f"send otp to{phone_number}: {code}")
    # SMS ...
    return True



# when support team answer the ticket send sms for user :
@shared_task
def send_ticket_notification(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        print(f"answer to ticket{ticket.dashboard.user.phone_number}")
        # SMS ...
    except:
        pass
    return True



# for group registeration :
@shared_task
def send_group_invitation(phone_number):
    print(f"group inviting{phone_number}")
    return True



# remove expired otp :
@shared_task
def cleanup_expired_otps():
    expired_time = timezone.now() - timedelta(minutes=10)
    OTP.objects.filter(created_at__lt=expired_time).delete()
    return True



# when online course finished the recorded vidios convert to offline course :  
@shared_task
def convert_online_to_offline_course(course_id):
    try:
        course = Course.objects.get(id=course_id, type='online')
        if course.end_date and course.end_date < timezone.now():
            offline_course = Course.objects.create(
                title=f"{course.title} (recorded)",
                description=course.description,
                category=course.category,
                type='offline',
                base_price=course.base_price,
                final_price=course.final_price,
                access_days=30,
                is_active=True
            )
            # inactivation of course
            course.is_active = False
            course.save()
            # converting 
            for chapter in course.chapters.all():
                new_chapter = Chapter.objects.create(
                    course=offline_course,
                    title=chapter.title,
                    order=chapter.order
                )
                for video in chapter.videos.all():
                    Video.objects.create(
                        chapter=new_chapter,
                        title=video.title,
                        order=video.order,
                        file=video.file,
                        duration=video.duration
                    )
            # inactivation course for users
            Enrollment.objects.filter(course=course).update(is_active=False)
            
    except Course.DoesNotExist:
        pass
    return True