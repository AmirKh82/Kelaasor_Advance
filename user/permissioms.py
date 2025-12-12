"""
different permissions for user types
"""
from rest_framework.permissions import BasePermission



class Is_Regular_User(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'user'



class Is_Support_Team(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'support_team'



class Is_Educational_Support(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role == 'support_team' and 
                request.user.support_team_type == 'edu')



class Is_Financial_Support(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role == 'support_team' and 
                request.user.support_team_type == 'finance')



class Is_Admin_Support(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role == 'support_team' and 
                request.user.support_team_type == 'admin')



class Has_Complete_Data(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_data_complete



class Has_Verified_Phone(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.phone_verified



class Can_Purchase(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.phone_verified and user.user_data_complete