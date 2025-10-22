from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UnifiedTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    serializer = UnifiedTokenObtainPairSerializer(data = request.data)
    serializer.is_valid(raise_exception = True)
    return Response(serializer.validated_data , status = status.HTTP_200_OK)