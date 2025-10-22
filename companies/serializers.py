from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CompanyTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Invalid credentials provided. Please check username and password.'
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        if not hasattr(self.user, 'company_profile'):
            raise serializers.ValidationError(
                {"detail": "This login is for company owners only."}
            )

        return data

class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Company
        fields = ['id', 'owner', 'name', 'image', 'location', 'phone_number', 'description', 'email', 'website', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class CompanySignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Company
        fields = ['username', 'password', 'password2', 'email', 'name', 'image', 'location', 'phone_number', 'description', 'website']
        extra_kwargs = {
            'name': {'validators': []},
            'phone_number': {'validators': []},
            'email': {'validators': []},
        }
    def validate(self, data):
        errors = {}
        if not data.get('username'):
            errors['username'] = 'This field may not be blank.'
        elif User.objects.filter(username=data['username']).exists():
            errors['username'] = 'A user with that username already exists.'
        if not data.get('email'):
            errors['email'] = 'This field may not be blank.'
        else:
            if User.objects.filter(email=data['email']).exists():
                errors['email'] = 'This email is already associated with another user.'
            if Company.objects.filter(email=data['email']).exists():
                errors['email'] = 'This email is already associated with another company.'
        if not data.get('password') or not data.get('password2'):
            errors['password'] = 'Both password fields are required.'
        elif data['password'] != data['password2']:
            errors['password'] = 'The two password fields did not match.'
        if not data.get('name'):
            errors['name'] = 'Company name may not be blank.'
        elif Company.objects.filter(name=data['name']).exists():
            errors['name'] = 'A company with this name already exists.'
        if 'phone_number' in data and data.get('phone_number'):
            if Company.objects.filter(phone_number=data['phone_number']).exists():
                errors['phone_number'] = 'This phone number is already registered to another company.'
        if errors:
            raise serializers.ValidationError(errors)
        return data
        
    def create(self, validated_data):
        with transaction.atomic():
            user_data = {
                'username': validated_data.pop('username'),
                'password': validated_data.pop('password')
            }
            validated_data.pop('password2')
            user = User.objects.create_user(**user_data)
            company = Company.objects.create(owner=user, **validated_data)
            return company

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True , write_only = True)
    new_password = serializers.CharField(required = True , write_only = True)
    new_password2 = serializers.CharField(required = True , write_only = True)

    def validate_old_password(self , value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password incorrect")
        return value

    def validate(self , data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password    ":"Your Passwords not match"})
        return data

    def save(self , **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user