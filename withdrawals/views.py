from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,AllowAny
from .models import Withdrawal
from .serializers import WithdrawalSerializer ,WithdrawalCreateSerializer
from .permissions import IsCompanyOrEmployee
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from salaries.models import MonthlyPayslip



@api_view(['POST'])
@permission_classes([IsCompanyOrEmployee , IsAuthenticated])
def create_withdrawal(request):
    employee = request.user.employee_profile
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year

    try:
        payslip = MonthlyPayslip.objects.get(
            salary_contract__employee=employee,
            month=current_month,
            year=current_year
        )
    except MonthlyPayslip.DoesNotExist:
        return Response({"detail": "لا يوجد كشف راتب متاح لك هذا الشهر."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = WithdrawalCreateSerializer(data=request.data)
    if serializer.is_valid():
        new_amount = serializer.validated_data['amount']
        allowed_percentage = payslip.salary_contract.withdraw_allowed_percentage
        allowed_amount = payslip.base_monthly_salary * (Decimal(allowed_percentage) / 100)
        total_withdrawn = Withdrawal.objects.filter(payslip=payslip).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        if (total_withdrawn + new_amount) > allowed_amount:
            remaining_amount = allowed_amount - total_withdrawn
            return Response(
                {"detail": f"your money order is more than allowed {remaining_amount}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        withdrawal = serializer.save(payslip=payslip)
        response_serializer = WithdrawalSerializer(withdrawal)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated ,IsCompanyOrEmployee])
def get_all_withdrawals (request):
    user = request.user 
    if hasattr(user, 'employee_profile'):
        payslips = MonthlyPayslip.objects.filter(salary_contract__employee=user.employee_profile)
        withdrawals = Withdrawal.objects.filter(payslip__in=payslips)
    elif hasattr(user, 'company_profile'):
        payslips = MonthlyPayslip.objects.filter(salary_contract__company=user.company_profile)
        withdrawals = Withdrawal.objects.filter(payslip__in=payslips)
    else:
        return Response({"detail": "User has no employee or company profile."}, status=status.HTTP_403_FORBIDDEN)

    serializer = WithdrawalSerializer(withdrawals, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsCompanyOrEmployee])
def get_withdrawal_summery(request):
    employee = request.user.employee_profile
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    try:
        payslip = MonthlyPayslip.objects.get(
            salary_contract__employee=employee,
            month=current_month,
            year=current_year
        )
    except MonthlyPayslip.DoesNotExist:
            return Response({"detail": "you dont have any contract for this month"}, status=status.HTTP_404_NOT_FOUND)
    allowed_percentage_rate = payslip.salary_contract.withdraw_allowed_percentage
    allowed_amount = payslip.base_monthly_salary * (Decimal(allowed_percentage_rate) / 100)
    total_withdrawn = Withdrawal.objects.filter(payslip=payslip).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    remaining_amount = allowed_amount - total_withdrawn
    if allowed_amount > 0:
            withdrawn_percentage = round((total_withdrawn / allowed_amount) * 100, 2)
            remaining_percentage = round((remaining_amount / allowed_amount) * 100, 2)
    else:
        withdrawn_percentage = Decimal('0.00')
        remaining_percentage = Decimal('0.00')
    summary_data = {
        'monthly_salary': payslip.base_monthly_salary,
        'allowed_withdrawal_limit': allowed_amount,
        'total_withdrawn_amount': total_withdrawn,
        'remaining_amount_for_withdrawal': remaining_amount,
        'withdrawn_percentage': f"{withdrawn_percentage}%",
        'remaining_percentage': f"{remaining_percentage}%",
    }

    return Response(summary_data, status=status.HTTP_200_OK)
