from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh = request.data.get('refresh')
        token = RefreshToken(refresh)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(
            {"detail": "Invalid refresh token."},
            status=status.HTTP_400_BAD_REQUEST
        )

