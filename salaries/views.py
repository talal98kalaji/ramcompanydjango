from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SalaryContract, MonthlyPayslip
from .serializers import (
    SalaryContractSerializer,
    SalaryContractDetailSerializer,
    MonthlyPayslipSerializer,
    SalaryAdjustmentCreateSerializer
)
from employees.permissions import IsCompanyOwner

# --- 1. واجهات خاصة بعقود الرواتب (SalaryContract) ---

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def salary_contract_list(request):
    """
    [GET] لعرض قائمة بكل عقود الرواتب في شركة المدير الحالي.
    """
    company = request.user.company_profile
    contracts = SalaryContract.objects.filter(company=company)
    serializer = SalaryContractDetailSerializer(contracts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def salary_contract_create(request):
    """
    [POST] لإنشاء عقد راتب جديد لموظف في الشركة.
    """
    serializer = SalaryContractSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def salary_contract_detail(request, pk):
    """
    [GET] عرض تفاصيل عقد راتب معين.
    """
    try:
        contract = SalaryContract.objects.get(pk=pk, company=request.user.company_profile)
    except SalaryContract.DoesNotExist:
        return Response({"detail": "عقد الراتب غير موجود أو لا ينتمي لشركتك."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SalaryContractDetailSerializer(contract)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def salary_contract_update(request, pk):
    """
    [PUT/PATCH] تعديل عقد راتب معين.
    """
    try:
        contract = SalaryContract.objects.get(pk=pk, company=request.user.company_profile)
    except SalaryContract.DoesNotExist:
        return Response({"detail": "عقد الراتب غير موجود أو لا ينتمي لشركتك."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SalaryContractSerializer(
        instance=contract,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- 2. واجهات خاصة بكشوفات الرواتب الشهرية (MonthlyPayslip) ---
# (هذه الواجهة تبقى كما هي لأنها تخدم GET فقط)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def monthly_payslip_detail(request, pk):
    """
    [GET] عرض تفاصيل كشف راتب شهري معين.
    """
    try:
        payslip = MonthlyPayslip.objects.get(pk=pk, salary_contract__company=request.user.company_profile)
    except MonthlyPayslip.DoesNotExist:
        return Response({"detail": "كشف الراتب غير موجود أو لا ينتمي لشركتك."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MonthlyPayslipSerializer(payslip)
    return Response(serializer.data)


# --- 3. واجهات خاصة بحركات الراتب (SalaryAdjustment) ---
# (هذه الواجهة تبقى كما هي لأنها تخدم POST فقط)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCompanyOwner])
def add_salary_adjustment(request, payslip_pk):
    """
    [POST] إضافة حركة جديدة (حسم أو مكافأة) على كشف راتب شهري معين.
    """
    try:
        payslip = MonthlyPayslip.objects.get(pk=payslip_pk, salary_contract__company=request.user.company_profile)
    except MonthlyPayslip.DoesNotExist:
        return Response({"detail": "كشف الراتب الذي تحاول التعديل عليه غير موجود."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SalaryAdjustmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(payslip=payslip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

