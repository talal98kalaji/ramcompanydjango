from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Employee, EmploymentRequest
from companies.models import Company
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):

    default_error_messages = {
        'no_active_account': 'Invalid credentials provided. Please check username and password.'
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        if not hasattr(self.user, 'employee_profile'):
            raise serializers.ValidationError(
                {"detail": "This login is for employees only."}
            )

        return data


class EmployeeSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    company = serializers.IntegerField()
    submitted_code = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        A comprehensive validation function for employee sign-up.
        """
        errors = {}
        if not data.get('username'):
            errors['username'] = 'This field may not be blank.'
        elif User.objects.filter(username=data['username']).exists():
            errors['username'] = 'A user with this username already exists.'
        if not data.get('email'):
            errors['email'] = 'This field may not be blank.'
        elif User.objects.filter(email=data['email']).exists():
            errors['email'] = 'A user with this email already exists.'
        if not data.get('password'):
            errors['password'] = 'This field may not be blank.'
        company_id = data.get('company')
        if not company_id:
            errors['company'] = 'Company ID is required.'
        elif not Company.objects.filter(pk=company_id).exists():
            errors['company'] = 'No company found with the provided ID.'

        if errors:
            raise serializers.ValidationError(errors)
            
        return data

    def create(self, validated_data):
        with transaction.atomic():
            user_data = {
                'username': validated_data['username'],
                'password': validated_data['password'],
                'email': validated_data['email'],
                'first_name': validated_data.get('first_name', ''),
                'last_name': validated_data.get('last_name', '')
            }
            
            user = User.objects.create_user(**user_data)            
            employee = Employee.objects.create(user=user)
            company_id = validated_data['company']
            company = Company.objects.get(pk=company_id)
            EmploymentRequest.objects.create(
                employee=employee,
                company=company,
                submitted_code=validated_data.get('submitted_code', ''),
                status='pending'
            )
            
            return validated_data

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user', 'company']

class EmploymentRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True) 
    company = serializers.StringRelatedField()
    processed_by = serializers.StringRelatedField()
    class Meta:
        model = EmploymentRequest
        fields = ['id', 'employee', 'company', 'submitted_code', 'status', 'created_at', 'processed_by']

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
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        super().update(instance, validated_data)
        return instance

class OnlyEmploymentRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    submitted_code = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_company_id(self, value):
        if not Company.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Company with this ID does not exist.")
        return value