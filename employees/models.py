from django.db import models
from django.contrib.auth.models import User
from companies.models import Company

class Employee(models.Model):
    user = models.OneToOneField(User, related_name="employee_profile", on_delete=models.CASCADE)
    
    # --- هذا هو التعديل الرئيسي ---
    # نجعل الشركة اختيارية (يمكن أن تكون فارغة) حتى تتم الموافقة على الطلب
    company = models.ForeignKey(Company, related_name="employees", on_delete=models.SET_NULL, null=True, blank=True)
    
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class EmploymentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requests')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employment_requests')
    submitted_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')

    def __str__(self):
        return f"Request from {self.employee.user.username} for {self.company.name}"

    

