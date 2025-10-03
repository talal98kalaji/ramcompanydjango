from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    def has_object_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'employee_profile')

class IsCompanyOrEmployee(BasePermission):
    def has_object_permission(self , request , view):
        if hasattr(request.user , "empolyee_profile"):
            if obj_payslip.salary_contract.employee == request.user.employee_profile:
                return True
        return ("Error with your Request Permission")

        if hasattr(request.user , "company_profile"):
            if obj.payslib.salary_contract.company == request.user.company_profile :
                return True
        return ("Error with your Request Permission")