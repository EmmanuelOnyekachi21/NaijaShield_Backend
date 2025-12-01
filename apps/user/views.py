from rest_framework import status
from rest_framework.response import Response
from apps.user.models import User
from rest_framework.decorators import api_view
from apps.user.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

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
