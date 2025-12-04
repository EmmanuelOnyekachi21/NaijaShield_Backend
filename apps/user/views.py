from rest_framework import status
from rest_framework.response import Response

from apps.user.models import User
from apps.user.models import TrustBadge

from rest_framework.decorators import api_view, permission_classes, parser_classes
from apps.user.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

import cloudinary.uploader

from django.utils import timezone

from apps.user.serializers import ProfileUpdateSerializer
from apps.user.serializers import BadgeStatusSerializer

from django.contrib.gis.geos import Point

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from apps.user.models import UserActivity
from apps.user.serializers import UserActivitySerializer
from apps.user.utils import log_user_activity

VERIFICATION_STEPS = [
    {
        "type": "id_verification",
        "status": "pending",  # default; override dynamically if verified
        "description": "Upload government ID for verification",
        "action": "Upload ID"
    },
    {
        "type": "location_verification",
        "status": "pending",
        "description": "Verify your farm/business location",
        "action": "Verify Location"
    }
]

BADGE_BENEFITS = {
    "new_user": {
        "current": ["Basic marketplace access", "Direct messaging", "Price tracking"],
        "next_level": ["Featured listing eligibility", "Priority in search results", "Access to premium buyers"]
    },
    "bronze": {
        "current": ["Featured listing eligibility", "Priority in search results", "Access to premium buyers"],
        "next_level": ["Prominent placement in search", "Higher buyer trust", "Access to premium tools"]
    },
    "silver": {
        "current": ["Prominent placement in search", "Higher buyer trust", "Access to premium tools"],
        "next_level": ["Diamond-level promotions", "Exclusive events", "Priority support"]
    },
    "gold": {
        "current": ["Diamond-level promotions", "Exclusive events", "Priority support"],
        "next_level": ["Diamond-level rewards and recognition"]
    },
    "diamond": {
        "current": ["Diamond-level rewards and recognition"],
        "next_level": []
    }
}

# Badge order for next-level calculation
BADGE_ORDER = ["new_user", "bronze", "silver", "gold", "diamond"]


@api_view(['GET'])
def user(request, public_id):
    if public_id:
        user = User.objects.get_object_by_public_id(public_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Public ID not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_profile(request):
    """
    PATCH /api/auth/profile/
    Accepts multipart/form-data or JSON. Validates inputs, uploads photo to Cloudinary, saves fields,
    enforces role-specific rules, and returns updated user data including profile_completion.
    """
    user = request.user
    serializer = ProfileUpdateSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {"error":serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    data = serializer.validated_data
    errors = {}

    #---------------- Role specific validation --------------------------#
    role = (user.role or "").lower()

    if "farm_size" in data and data.get('farm_size') is not None and role != "farmer":
        errors['farm_size'] = ["This field is only for farmers"]
    
    if "business_name" in data and data.get('business_name') is not None and role not in ['buyer', 'co-ops']:
        errors['business_name'] = ["This field is only for buyers and co-ops"]
    
    if errors:
        return Response(
            {"error": errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # -------------------- Handle Co-ordinates (convert to Point) --------------------------#
    location_lat = data.get("location_lat", None)
    location_lng = data.get("location_lng", None)
    location_text = data.get("location_text", None)
    
    if location_lat is not None and location_lng is not None:
        # GeoDjango Point expects (x=lng, y=lat)
        try:
            point = Point(float(location_lng), float(location_lat), srid=4326)
            user.location = point
        except Exception as e:
            return Response(
                {"error": {'location': ["Invalid coordinates"]}},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # --- Handle simple scalar fields ---
    if "location_text" in data:
        user.location_text = data.get("location_text")

    if "farm_size" in data:
        user.farm_size = data.get("farm_size")

    if "business_name" in data:
        user.business_name = data.get("business_name")

    if "bio" in data:
        user.bio = data.get("bio")

    if "email" in data:
        user.email = data.get("email")
    
    # ------------------- handle profile_photo upload to Cloudinary --------------------------#
    photo_file = request.FILES.get('profile_photo') or data.get('profile_photo')
    if photo_file:
        try:
            # Upload to cloudinary
            result = cloudinary.uploader.upload(
                photo_file,
                folder=f"users/{user.public_id}/profile_photo",
                public_id=f"profile_{user.public_id}",
                overwrite=True,
                resource_type="image",
                use_filename=False,
                unique_filename=True,
                invalidate=True
            )
            secure_url = result.get('secure_url')
            if not secure_url:
                return Response({"error": {"profile_photo": ["Upload failed"]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user.profile_photo = secure_url
        except Exception as exc:
            # Cloudinary upload failed
            return Response({"error": {"profile_photo": [str(exc)]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Save user
    user.updated_at = timezone.now()
    user.save()

    # Build response payload
    serializer = UserSerializer(user)

    log_user_activity(
        request,
        user=user,
        action_type=UserActivity.ActionTypes.UPDATE,
        description="User updated successfully",
        metadata={
            "user_id": str(user.public_id),
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role
        }
    )

    return Response(serializer.data, status=status.HTTP_200_OK)    


class UserSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    user = request.user
    role = request.query_params.get('role', '')
    search_query = request.query_params.get('search', '')
    lat = request.query_params.get('location_lat')
    lng = request.query_params.get('location_lng')
    radius = request.query_params.get('radius', 50)

    queryset = User.objects.all().exclude(public_id=user.public_id)

    if role:
        queryset = queryset.filter(role__iexact=role)
    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # ---------------- Geo Search --------------------
    user_point = None
    if lat and lng:
        try:
            user_point = Point(float(lng), float(lat), srid=4326)

            queryset = (
                queryset.filter(location__distance_lte=(user_point, D(km=float(radius))))
                .annotate(distance=Distance('location', user_point))
                .order_by('distance')
            )
        except ValueError:
            return Response({"error": {"location": ["Invalid lat/lng format"]}}, status=400)

    # ----- Pagination -----
    paginator = UserSearchPagination()
    page = paginator.paginate_queryset(queryset, request)

    results = []

    for u in page:
        res = {
            'id': u.public_id,
            'full_name': u.get_full_name(),
            'role': u.role,
            'location_text': u.location_text,
            'profile_photo': u.profile_photo,
            'trust_badge': 'New User',
            'location': u.location,
            'profile_completion': u.profile_completion,
            'days_since_joined': (timezone.now() - u.created_at).days
        }

        # Include distance only if present
        if user_point and hasattr(u, 'distance'):
            res['distance'] = u.distance
        results.append(res)
    
    return paginator.get_paginated_response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def badge_status(request):
    user = request.user

    try:
        badge = user.badge
    except TrustBadge.DoesNotExist:
        return Response({"error": "Badge not found for user"}, status=404)
    
    serializer = BadgeStatusSerializer(badge)

    # Calculate the next badge and transactions needed
    badge_level = badge.badge_level
    current_index = BADGE_ORDER.index(badge_level)
    next_badge = BADGE_ORDER[current_index + 1] if current_index < len(BADGE_ORDER) - 1 else badge_level

    # For demonstration, define transactions required for next badge
    TRANSACTION_REQUIREMENTS = {
        "new_user": 5,
        "bronze": 20,
        "silver": 50,
        "gold": 100,
        "diamond": 200
    }

    transactions_needed = max(0, TRANSACTION_REQUIREMENTS.get(next_badge) - badge.transaction_count)

    steps = []
    for step in VERIFICATION_STEPS:
        s = step.copy()

        if s['type'] == 'id_verification':
            s['status'] = 'completed' if badge.is_id_verified else 'pending'
        elif s['type'] == "location_verification":
            s['status'] = "completed" if badge.is_location_verified else "pending"
        steps.append(s)
    
    response_data = {
        "current_badge": badge.badge_level,
        "badge_display": badge.get_badge_display_name(),
        "verifications": {
            "phone_verified": badge.is_phone_verified,
            "id_verified": badge.is_id_verified,
            "location_verified": badge.is_location_verified,
            "community_trusted": badge.is_community_trusted
        },
        "transaction_stats": {
            "total_transactions": badge.transaction_count,
            "average_rating": float(badge.average_rating or 0),
            "next_badge": next_badge,
            "transactions_needed": transactions_needed
        },
        "verification_steps": steps,
        "benefits": BADGE_BENEFITS.get(badge.badge_level, {"current": [], "next_level": []})
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity(request):
    """
    GET /api/users/activity/?page=1&action_type=login
    Returns authenticated user's activity logs.
    """
    user = request.user

    # --------------- FILTERING --------------- #
    action_type = request.query_params.get('action_type', '')

    queryset = UserActivity.objects.filter(
        user=user,
        action_type=action_type if action_type else None
    )
    # Most recent first
    queryset = queryset.order_by('-created_at')
    
    # ----- Pagination -----
    paginator = PageNumberPagination()
    paginator.page_size = 50
    paginated_qs = paginator.paginate_queryset(queryset, request)

    serializer = UserActivitySerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serializer.data)







