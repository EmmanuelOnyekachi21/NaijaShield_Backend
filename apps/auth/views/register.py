from rest_framework import status
from rest_framework.response import Response
from apps.auth.serializers.register import RegisterSerializer
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.serializers import UserSerializer
from apps.user.utils import log_user_activity
from apps.user.models import UserActivity

@api_view(['POST'])
def register_user(request):
    """
    Register a new user.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    log_user_activity(
        request,
        user=user,
        action_type=UserActivity.ActionTypes.REGISTER,
        description="User registered successfully",
        metadata={
            "user_id": str(user.public_id),
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role
        }
    )
    return Response(
        {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        },
        status=status.HTTP_201_CREATED
    )
