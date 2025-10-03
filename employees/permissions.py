from rest_framework.permissions import BasePermission


class IsSelfOrCompanyOrAdmin(BasePermission):
    def has_object_permission(self , request  , view , obj):
        if request.user.is_staff:
            return True
        if request.user == obj.user:
            return True
        if  obj.company and request.user == obj.company.owner :
            return True
        return False

class IsCompanyOwner(BasePermission):
    def has_permission(self , request ,view):
        return request.user.is_authenticated and hasattr(request.user, 'company_profile')