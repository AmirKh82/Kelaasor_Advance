import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kelaasor_Advance.settings')

app = Celery('Kelaasor_Advance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# # Kelaasor_Advance/celery.py
# try:
#     from celery import Celery
#     CELERY_INSTALLED = True
# except ImportError:
#     CELERY_INSTALLED = False
#     print("⚠️ Celery is not installed. Running without Celery.")

# if CELERY_INSTALLED:
#     import os
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kelaasor_Advance.settings')
#     app = Celery('Kelaasor_Advance')
#     app.config_from_object('django.conf:settings', namespace='CELERY')
#     app.autodiscover_tasks()
# else:
#     # ایجاد یک fake app برای جلوگیری از ارور
#     class FakeCelery:
#         def task(self, *args, **kwargs):
#             def decorator(func):
#                 return func
#             return decorator
#     app = FakeCelery()