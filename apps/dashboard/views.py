from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.user.models import User
from apps.user.serializers import UserSerializer
from django.db.models import Sum
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    role = user.role.lower()
    days_since_joined = (timezone.now() - user.created_at).days
    profile_completion = getattr(user, "profile_completion", 0)
    
    if role == 'farmer':
        stats = {
            "active_listings": 0,
            "total_sales": 0,
            "total_revenue": 0,
            "messages_unread": 0,
            "views_this_week": 0,
            "trust_badge": "New User",
            "days_since_joined": days_since_joined
        }
        quick_actions = [
            {"label": "Create Listing", "route": "/listings/create"},
            {"label": "Check Prices", "route": "/prices"},
            {"label": "Complete Profile", "route": "/profile"}
        ]
    
    elif role == 'buyer':
        stats = {
            "active_searches": 0,
            "total_purchases": 0,
            "suppliers_contacted": 0,
            "messages_unread": 0,
            "trust_badge": "New User",
            "days_since_joined": days_since_joined
        }
        quick_actions = [
            {"label": "Find Produce", "route": "/marketplace"},
            {"label": "Check Prices", "route": "/prices"},
            {"label": "My Purchases", "route": "/purchases"}
        ]
    elif role == 'co-ops':
        stats = {
            "member_count": 0,
            "total_listings": 0,
            "total_sales": 0,
            "messages_unread": 0,
            "trust_badge": "New User",
            "days_since_joined": days_since_joined
        }
        quick_actions = [
            {"label": "Add Members", "route": "/cooperative/members"},
            {"label": "View Reports", "route": "/cooperative/reports"}
        ]
    else:
        stats = {}
        quick_actions = []

    return Response({
        "role": role,
        "profile_completion": profile_completion,
        "stats": stats,
        "quick_actions": quick_actions
    })


