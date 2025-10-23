from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UnifiedTokenObtainPairSerializer
from companies.serializers import CompanySerializer
from employees.serializers import EmployeeSerializer
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    serializer = UnifiedTokenObtainPairSerializer(data = request.data)
    serializer.is_valid(raise_exception = True)
    return Response(serializer.validated_data , status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def about_me(request):
    user = request.user
    user_type = None
    profile_data = None
    serializer = None

    if hasattr(user , 'company_profile'):
        user_type = 'company'
        profile = user.company_profile
        serializer =CompanySerializer(profile)
        profile_data = serializer.data
    
    elif hasattr(user , 'employee_profile'):
        user_type = "employee"
        profile = user.employee_profile
        serializer = EmployeeSerializer(profile)
        profile_data = serializer.data
    elif user.is_superuser:
             user_type = 'superuser'
             profile_data = {
                 'id': user.id,
                 'username': user.username,
                 'email': user.email,
                 'is_superuser': True
             }
    else:
        return Response( {"detail": "User profile not found."},status=status.HTTP_404_NOT_FOUND)
    response_data = {
        'user_type': user_type,
        'profile': profile_data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_self(request):
    user = request.user
    profile_instance = None
    serializer_class = None
    if hasattr(user, 'company_profile'):
        profile_instance = user.company_profile
        serializer_class = CompanySerializer 
    elif hasattr(user, 'employee_profile'):
        profile_instance = user.employee_profile
        serializer_class = EmployeeUpdateSerializer
    else:
        return Response({"detail": "No profile found for this user."}, status=status.HTTP_400_BAD_REQUEST)
    partial_update = request.method == 'PATCH'
    serializer = serializer_class(
        instance=profile_instance, 
        data=request.data, 
        partial=partial_update,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)