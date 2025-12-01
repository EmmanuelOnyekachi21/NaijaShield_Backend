from rest_framework import status
from rest_framework.response import Response
from apps.auth.serializers.register import RegisterSerializer
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.serializers import UserSerializer


@api_view(['POST'])
def register_user(request):
    """
    Register a new user.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        },
        status=status.HTTP_201_CREATED
    )
