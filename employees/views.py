from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import AllowAny , IsAdminUser , IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChangePasswordSerializer,EmployeeSignUpSerializer, EmploymentRequestSerializer,EmployeeSerializer,OnlyEmploymentRequestSerializer ,EmployeeTokenObtainPairSerializer 
from .models import Employee , EmploymentRequest
from .permissions import IsSelfOrCompanyOrAdmin , IsCompanyOwner
from companies.models import Company

@api_view(['POST'])
@permission_classes([AllowAny])
def register_employee(request):
    serializer = EmployeeSignUpSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data , status = status.HTTP_201_CREATED)
    return Response(serializer.errors , status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def employee_login(request):
    serializer = EmployeeTokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, (IsAdminUser | IsCompanyOwner)])
def get_all_employees(request):
    if request.user.is_staff:
        employees = Employee.objects.filter(company__isnull=False)
    elif hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
        employees = Employee.objects.filter(company=company)
    else:
        employees = Employee.objects.none()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSelfOrCompanyOrAdmin])
def get_employee_by_id(request , employee_id):
    try:
        employee = Employee.objects.get(pk = employee_id)
    except Employee.DoesNotExist:
        return Response({"detail" : "Employee not found"} , status = status.HTTP_404_NOT_FOUND)
    request.parser_context['view'].check_object_permissions(request , employee)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data , status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsCompanyOwner | IsAdminUser])
def get_employee_by_name(request):
    name_query = request.query_params.get('name' , '')
    company = request.user.company_profile
    employees = Employee.objects.filter(company = company , user__username__icontains = name_query)
    serializer = EmployeeSerializer(employees , many = True)
    return Response(serializer.data , status = status.HTTP_200_OK)

@api_view(['PUT' , 'PATCH'])
@permission_classes([IsSelfOrCompanyOrAdmin])
def update_employee(request , employee_id):
    try:
        employee = Employee.objects.get(pk = employee_id)
    except Employee.DoesNotExist:
        return Response({"detail" : "Employee not found"} , status = status.HTTP_404_NOT_FOUND)
    serializer = EmployeeUpdateSerializer(
        instance = employee, data = request.data ,
        partial = request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data , status = status.HTTP_200_OK)
    return Response(serializer.errors , status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data = request.data , context = {"request" :  request })
    if serializer.is_valid():
        serializer.save()
        return Response({"detail" : "Password has been updated successfully"})
    return Response(serializer.errors , status = status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsSelfOrCompanyOrAdmin])
def delete_employee(request , employee_id):
    try:
        employee = Employee.objects.get(pk = employee_id)
    except Employee.DoesNotExist:
        return Response({"detail" : "Employee not found"} , status = status.HTTP_404_NOT_FOUND)
    request.parser_context['view'].check_object_permissions(request , employee)
    user_to_delete = employee.user
    user_to_delete.delete()
    return Response({"detail" : "Employee deleted successfully"} , status = status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsCompanyOwner])
def list_pending_requests (request):
    company = request.user.company_profile
    pending_requests = EmploymentRequest.objects.filter(company = company , status = 'pending')

    serializer = EmploymentRequestSerializer(pending_requests , many = True)
    return Response(serializer.data , status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def accept_employment_request(request ,pk):
    try:
        request_to_approve = EmploymentRequest.objects.get(pk=pk)
    except EmploymentRequest.DoesNotExist:
        return Response({'detail': 'Request not Found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user != request_to_approve.company.owner:
        return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    if request_to_approve.status != 'pending':
        return Response({"detail": "This request has already been processed."}, status=status.HTTP_400_BAD_REQUEST)
    
    request_to_approve.status = 'approved'
    request_to_approve.processed_by = request.user
    request_to_approve.save()
    employee = request_to_approve.employee
    employee.company = request_to_approve.company 
    employee.save()
    return Response({"detail": "This request has been approved successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def reject_employment_request(request , pk):
    try:
        reject_request = EmploymentRequest.objects.get(pk = pk )
    except:
        Response({"detail":"this request doesnt here anymore"})
    if request.user != reject_request.company.owner:
        return Response({"detail":"you don't have permission to do this Reject"})
    if reject_request.status != 'pending':
        return Response({"detail" : "this Request doesnt here anymore"} , status=status.HTTP_400_BAD_REQUEST)
    reject_request.status = 'rejected'
    reject_request.processed_by = request.user
    reject_request.save()
    return Response({"detail" : "this request has rejected"} , status = status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def create_employment_request(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return Response({"detail": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)
    if employee.company is not None:
        return Response(
            {"detail": f"You are already employed with {employee.company.name}. You cannot apply for a new job."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if EmploymentRequest.objects.filter(employee=employee, status='pending').exists():
        return Response(
            {"detail": "You already have a pending employment request."},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = OnlyEmploymentRequestSerializer(data=request.data)
    if serializer.is_valid():
        company_id = serializer.validated_data['company_id']
        submitted_code = serializer.validated_data.get('submitted_code', '')
        company = Company.objects.get(pk=company_id)
        EmploymentRequest.objects.create(
            employee=employee,
            company=company,
            submitted_code=submitted_code,
            status='pending'
        )
        return Response(
            {"detail": "Your new employment request has been sent successfully."},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)