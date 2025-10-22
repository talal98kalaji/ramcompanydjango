from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class UnifiedTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Invalid Username Or Password"
    }
    def validate(self , attrs):
        data =super().validate(attrs)
        user = self.user
        user.type = None
        profile_id = None

        if user.is_superuser:
            user_type = "superuser"
            profile_id = user.id
        elif hasattr(user , "company_profile"):
            user_type = "company"
            profile_id = user.company_profile.id
        elif hasattr(user , "employee_profile"):
            user_type = "employee"
            profile_id = user.employee_profile.id
        else :
            raise serializers.ValidationError(
                {"detail" : "No User account type"}
            )

        data['user_type'] = user_type
        data['username'] = user.username
        data['profile_id'] = profile_id
        return data
