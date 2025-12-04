from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.utils import log_user_activity
from apps.user.models import UserActivity

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh = request.data.get('refresh')
        token = RefreshToken(refresh)
        token.blacklist()
        log_user_activity(
            request,
            user=request.user,
            action_type=UserActivity.ActionTypes.LOGOUT,
            description="User logged out successfully",
            metadata={
                "user_id": str(request.user.public_id),
                "email": request.user.email,
                "phone_number": request.user.phone_number,
                "role": request.user.role
            }
        )
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(
            {"detail": "Invalid refresh token."},
            status=status.HTTP_400_BAD_REQUEST
        )

