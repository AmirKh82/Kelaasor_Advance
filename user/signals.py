"""
signals of user registeration 
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Dashboard, Wallet, Basket

User = get_user_model()



# when user registers complete create dasbord for user that includes wallet and basket in first :
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        dashboard = Dashboard.objects.create(user=instance)
        Wallet.objects.create(dashboard=dashboard)
        Basket.objects.create(dashboard=dashboard)
