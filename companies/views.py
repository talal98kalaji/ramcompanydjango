from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Company
from .serializers import CompanySerializer, CompanySignUpSerializer ,CompanyTokenObtainPairSerializer,ChangePasswordSerializer
from .permissions import IsOwnerOrReadOnly


@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request):
    serializer = CompanySignUpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def company_login(request):
    serializer = CompanyTokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)    
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_companies(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_by_id(request, company_id):
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return Response({detail :"Company not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = CompanySerializer(company)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) 
def delete_company_profile(request, pk):
    try:
        company_to_delete = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response( {"detail": "no company"}, status=status.HTTP_404_NOT_FOUND)
    is_owner = (request.user == company_to_delete.owner)
    is_admin = (request.user.is_staff)
    if not is_owner and not is_admin:
        return Response(
            {"detail": "company not found"}, status=status.HTTP_403_FORBIDDEN)
    if is_admin:
        company_to_delete.delete() 
        return Response( {"detail": "company has deleted"}, status=status.HTTP_204_NO_CONTENT)
    else:
        company_to_delete.soft_delete()
        return Response(
            {"detail": "Company will be deleted after 30 days"},
            status=status.HTTP_200_OK)



@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
def update_company(request):
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        return Response({detail :"No User's Company "},status = status.HTTP404_NOT_FOUND)
    serializer = CompanySerializer(company, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data = request.data , context = {"request" : request})
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "password updated successfuly"})
    return Response(serializer.errors , status =status.HTTP_400_BAD_REQUEST)