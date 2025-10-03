from rest_framework import serializers
from .models import Withdrawal

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'payslip', 'amount','date']
        read_only_fields = ['id', 'date']

    def validate(self, data):
        payslip = data.get('payslip')
        amount = data.get('amount')

        if not payslip:
            raise serializers.ValidationError("Payslip is required.")

        allowed_percentage = payslip.salary_contract.withdraw_allowed_percentage
        allowed_amount = payslip.base_monthly_salary * (allowed_percentage / 100)

        if amount > allowed_amount:
            raise serializers.ValidationError(f"money amount its more than allowed{allowed_amount}")

        return data




class WithdrawalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer لإنشاء طلب سحب جديد.
    لا يتطلب إرسال كشف الراتب، حيث سيتم تحديده تلقائياً.
    """
    class Meta:
        model = Withdrawal
        fields = ['amount']


