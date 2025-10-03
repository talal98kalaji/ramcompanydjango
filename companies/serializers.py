from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company


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
            'email': {'required': False}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if 'email' in data and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return data
    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email', ''),
            'password': validated_data.pop('password')
            }
        validated_data.pop('password2')
        user = User.objects.create_user(**user_data)
        company = Company.objects.create(owner=user, **validated_data)
        return company

