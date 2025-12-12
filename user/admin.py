"""
admin panel
"""
from django.contrib import admin
from .models import User, OTP, Dashboard, Wallet, Basket, Basket_Item, Transaction, Enrollment, Purchased_Course, Ticket, Group_Registration, Group_Members



admin.site.register(User)
admin.site.register(OTP)
admin.site.register(Dashboard)
admin.site.register(Wallet)
admin.site.register(Basket)
admin.site.register(Basket_Item)
admin.site.register(Transaction)
admin.site.register(Enrollment)
admin.site.register(Purchased_Course)
admin.site.register(Ticket)
admin.site.register(Group_Registration)
admin.site.register(Group_Members)