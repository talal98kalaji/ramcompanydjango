from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from companies.models import Company
from employees.models import Employee
from django.utils import timezone
import datetime

class SalaryContract(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="salary_contract")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="salary_contracts")
    yearly_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    withdraw_allowed_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="النسبة المئوية من الراتب الشهري المسموح بسحبها"
    )
    
    @property
    def monthly_salary(self):
        return self.yearly_salary / 12

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs) 
        
        if is_new:
            current_year = timezone.now().year
            for month in range(1, 13):
                MonthlyPayslip.objects.create(
                    salary_contract=self,
                    month=month,
                    year=current_year,
                    base_monthly_salary=self.monthly_salary
                )

    def __str__(self):
        return f"عقد راتب لـ {self.employee.user.username}"


class MonthlyPayslip(models.Model):
    salary_contract = models.ForeignKey(SalaryContract, on_delete=models.CASCADE, related_name="payslips")
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField(validators=[MinValueValidator(2020)])
    base_monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('salary_contract', 'month', 'year')

    @property
    def total_additions(self):
        return sum(adj.amount for adj in self.adjustments.filter(adjustment_type='addition'))

    @property
    def total_deductions(self):
        return sum(adj.amount for adj in self.adjustments.filter(adjustment_type='deduction'))

    @property
    def final_salary(self):
        return self.base_monthly_salary + self.total_additions - self.total_deductions

    def __str__(self):
        return f"Salary statement for {self.salary_contract.employee.user.username} - شهر {self.month}/{self.year}"


class SalaryAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('addition', 'Addition'),
        ('deduction', 'Deduction'),
    ]
    payslip = models.ForeignKey(MonthlyPayslip, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_adjustment_type_display()} بقيمة {self.amount} لـ {self.payslip}"

