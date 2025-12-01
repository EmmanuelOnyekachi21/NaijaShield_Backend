from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.auth.serializers import LoginSerializer


@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)
