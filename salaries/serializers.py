from rest_framework import serializers
from .models import SalaryContract, MonthlyPayslip, SalaryAdjustment
from employees.models import Employee

# --- 1. Serializers خاصة بحركات الراتب (SalaryAdjustment) ---

class SalaryAdjustmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer لإنشاء حركة جديدة (إضافة أو حسم) على كشف راتب شهري.
    """
    class Meta:
        model = SalaryAdjustment
        # الـ payslip سيتم تحديده من الرابط (URL)، لذلك نحتاج فقط هذه الحقول
        fields = ['adjustment_type', 'amount', 'reason']


class SalaryAdjustmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض تفاصيل حركة راتب (للاستخدام داخل كشف الراتب).
    """
    class Meta:
        model = SalaryAdjustment
        fields = ['id', 'adjustment_type', 'amount', 'reason', 'created_at']


# --- 2. Serializers خاصة بكشف الراتب الشهري (MonthlyPayslip) ---

class MonthlyPayslipSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض تفاصيل كشف راتب شهري واحد.
    """
    # نقوم بتضمين كل حركات الراتب المرتبطة بهذا الكشف
    adjustments = SalaryAdjustmentDetailSerializer(many=True, read_only=True)
    
    # نقوم بعرض الخصائص المحسوبة من الموديل
    total_additions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = MonthlyPayslip
        fields = [
            'id', 'month', 'year', 
            'total_additions', 'total_deductions', 'final_salary',
            'adjustments'
        ]


# --- 3. Serializers خاصة بعقد الراتب (SalaryContract) ---

class SalaryContractSerializer(serializers.ModelSerializer):
    """
    Serializer لإنشاء أو تحديث عقد راتب لموظف.
    """
    # عند الإنشاء، سيتم تمرير رقم الموظف (ID)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = SalaryContract
        fields = ['id', 'employee', 'yearly_salary', 'withdraw_allowed_percentage']
        read_only_fields = ['id']

    def validate_employee(self, employee):
        """
        نتحقق من أن الموظف ليس لديه عقد راتب بالفعل (فقط عند الإنشاء).
        """
        # self.instance يكون None فقط في حالة الإنشاء
        if self.instance is None and SalaryContract.objects.filter(employee=employee).exists():
            raise serializers.ValidationError("هذا الموظف لديه عقد راتب مسجل بالفعل.")
        return employee

    def create(self, validated_data):
        """
        عند إنشاء العقد، يتم ربطه تلقائياً بالشركة التي يملكها المستخدم الحالي.
        """
        # self.context['request'] تسمح لنا بالوصول لمعلومات الطلب، مثل المستخدم
        company = self.context['request'].user.company_profile
        validated_data['company'] = company
        
        # دالة save في الموديل ستقوم بإنشاء كشوفات الرواتب تلقائياً
        contract = SalaryContract.objects.create(**validated_data)
        return contract


class SalaryContractDetailSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض التفاصيل الكاملة لعقد الراتب مع كل كشوفات الرواتب.
    """
    employee = serializers.StringRelatedField()
    company = serializers.StringRelatedField()
    monthly_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # نقوم بتضمين كل كشوفات الرواتب المرتبطة بهذا العقد
    payslips = MonthlyPayslipSerializer(many=True, read_only=True)

    class Meta:
        model = SalaryContract
        fields = [
            'id', 'employee', 'company', 
            'yearly_salary', 'monthly_salary', 'withdraw_allowed_percentage',
            'payslips'
        ]
