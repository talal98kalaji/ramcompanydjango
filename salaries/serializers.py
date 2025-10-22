from rest_framework import serializers
from .models import SalaryContract, MonthlyPayslip, SalaryAdjustment
from employees.models import Employee


class SalaryAdjustmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryAdjustment
        fields = ['adjustment_type', 'amount', 'reason']


class SalaryAdjustmentDetailSerializer(serializers.ModelSerializer):
    adjustment_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = SalaryAdjustment
        fields = ['adjustment_id', 'adjustment_type', 'amount', 'reason', 'created_at']


class MonthlyPayslipSerializer(serializers.ModelSerializer):
    payslip_id = serializers.IntegerField(source='id', read_only=True)
    adjustments = SalaryAdjustmentDetailSerializer(many=True, read_only=True)
    total_additions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = MonthlyPayslip
        fields = [
            'payslip_id', 'month', 'year', 
            'total_additions', 'total_deductions', 'final_salary',
            'adjustments'
        ]


class SalaryContractSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee')    
    contract_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = SalaryContract
        fields = ['contract_id', 'employee_id', 'yearly_salary', 'withdraw_allowed_percentage']
        read_only_fields = ['contract_id']

    def validate_employee(self, employee):
        intance = self.context.get('instance')
        if instance is None and SalaryContract.objects.filter(employee=employee).exists():
            raise serializers.ValidationError("This Employee has already Contract")
        return employee

    def create(self, validated_data):
        company = self.context['request'].user.company_profile
        validated_data['company'] = company
        contract = SalaryContract.objects.create(**validated_data)
        return contract


class SalaryContractDetailSerializer(serializers.ModelSerializer):
    contract_id = serializers.IntegerField(source='id', read_only=True)
    employee_username = serializers.CharField(source='employee.user.username', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    monthly_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payslips = MonthlyPayslipSerializer(many=True, read_only=True)
    
    class Meta:
        model = SalaryContract
        fields = [
                    'contract_id', 'employee_username', 'company_name',
                    'yearly_salary', 'monthly_salary', 'withdraw_allowed_percentage',
                    'payslips'
                ]



