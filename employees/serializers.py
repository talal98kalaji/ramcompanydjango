from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Employee, EmploymentRequest
from companies.models import Company

# --- الخطوة 1: ننشئ Serializer بسيط لعرض بيانات المستخدم ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

# --- Serializer تسجيل الموظف ---
# (تم تحسينه ليكون أكثر دقة)
class EmployeeSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    company = serializers.IntegerField() 
    submitted_code = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate_company_id(self, value):
        if not Company.objects.filter(pk=value).exists():
            raise serializers.ValidationError("This Company does not exist.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'password': validated_data['password'],
            'email': validated_data['email'],
            'first_name' : validated_data['first_name'],
            'last_name': validated_data ['last_name']
        }
        company = validated_data['company']
        submitted_code = validated_data.get('submitted_code', '')
        
        user = User.objects.create_user(**user_data)
        employee = Employee.objects.create(user=user)
        company = Company.objects.get(pk=company)
        
        EmploymentRequest.objects.create(
            employee=employee,
            company=company,
            submitted_code=submitted_code,
            status='pending'
        )
        return validated_data

# --- Serializer عرض الموظف (تم تصحيحه) ---
class EmployeeSerializer(serializers.ModelSerializer):
    # --- الخطوة 2: نستخدم UserSerializer هنا لعرض بيانات المستخدم كاملة ---
    user = UserSerializer(read_only=True)
    company = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Employee
        # الآن القائمة تحتوي فقط على الحقول الموجودة في موديل Employee
        fields = ['id', 'user', 'company']

# --- Serializer عرض طلب التوظيف (يبقى كما هو) ---
class EmploymentRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True) # نعرض بيانات الموظف كاملة
    company = serializers.StringRelatedField()
    processed_by = serializers.StringRelatedField()
    class Meta:
        model = EmploymentRequest
        fields = ['id', 'employee', 'company', 'submitted_code', 'status', 'created_at', 'processed_by']

# --- Serializer تحديث الموظف (تم تحسينه) ---
class EmployeeUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = ['phone_number',  'username', 'email', 'first_name', 'last_name', 'password']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))
            
        # تحديث بيانات المستخدم
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # تحديث بيانات الموظف (باستخدام super)
        super().update(instance, validated_data)
        return instance

class OnlyEmploymentRequestSerializer(serializers.Serializer):
    """
    Serializer مخصص للموظف الحالي لإرسال طلب توظيف جديد لشركة جديدة.
    """
    company_id = serializers.IntegerField()
    submitted_code = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_company_id(self, value):
        """
        يتحقق من أن الشركة المختارة موجودة.
        """
        if not Company.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Company with this ID does not exist.")
        return value