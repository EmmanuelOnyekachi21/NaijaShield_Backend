from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

@api_view(['POST'])
def refresh(request):
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    except TokenError as e:
        raise InvalidToken(e.args[0])
