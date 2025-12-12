from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Discount_Code
from .serializers import Discount_Code_Serializer
from user.models import Ticket, User, Enrollment
from user.serializers import Ticket_Serializer
from user.permissioms import Is_Admin_Support, Is_Educational_Support, Is_Financial_Support
from user.tasks import send_ticket_notification
from product.models import Course
from product.serializers import Course_Serializers



# ticket :
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = Ticket_Serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'status']
    
    # this func check permissions for user to get access :
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'reply', 'destroy']:
            return [Is_Admin_Support() | Is_Educational_Support() | Is_Financial_Support()]
        return [permissions.IsAuthenticated()]

    # this func answer the user ticket : 
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        message = request.data.get('message')  
        if not message:
            return Response({'error': 'mesege is neccery'})
        if ticket.department == 'general' and not request.user.support_team_type == 'admin':
            return Response({'error': 'just admin'})
        if ticket.department == 'edu' and request.user.support_team_type not in ['admin', 'edu']:
            return Response({'error': 'just admin and edu'})
        if ticket.department == 'finance' and request.user.support_team_type not in ['admin', 'finance']:
            return Response({'error': 'jusst admin and finance'})
        ticket.status = 'answered'
        ticket.save()
        send_ticket_notification.delay(ticket.id)
        return Response({'success': True})



# discount :
class Discount_Code_ViewSet(viewsets.ModelViewSet):
    queryset = Discount_Code.objects.all()
    serializer_class = Discount_Code_Serializer
    permission_classes = [Is_Admin_Support | Is_Financial_Support]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['scope', 'is_active', 'usage_type']



# Course Management :
class Course_Management_ViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = Course_Serializers
    permission_classes = [Is_Admin_Support | Is_Educational_Support]
    
    # this func manage user in course :
    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        course = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'user not found'})
        Enrollment.objects.get_or_create(
            dashboard=user.dashboard,
            course=course,
            defaults={
                'access_expires_at': timezone.now() + timezone.timedelta(days=30) if course.type == 'offline' else None,
                'is_active': True
            }
        )
        return Response({'success': True})
    
    # this func manage user in course : 
    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        course = self.get_object()
        user_id = request.data.get('user_id')  
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'user not found'})
        Enrollment.objects.filter(dashboard=user.dashboard, course=course).delete()
        return Response({'success': True})