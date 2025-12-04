from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.auth.serializers import LoginSerializer
from apps.user.utils import log_user_activity 
from apps.user.models import UserActivity, User


@api_view(['POST'])
def login_user(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # Log successful login
        log_user_activity(
            request,
            user=user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description="Login successful",
            metadata={
                "user_id": str(user.public_id),
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Log failed login
        log_user_activity(
            request,
            user=user,
            action_type=UserActivity.ActionTypes.LOGIN_FAILED,
            description="Login failed",
            metadata={
                "error": str(e),
                "payload": request.data.get("email") or request.data.get("phone_number")
            }
        )

        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )
