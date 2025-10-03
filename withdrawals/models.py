from django.db import models
from salaries.models import MonthlyPayslip
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Withdrawal (models.Model):
    payslip = models.ForeignKey(MonthlyPayslip , on_delete = models.PROTECT , related_name="withdrawals")
    amount = models.DecimalField(max_digits=10 , decimal_places=2)
    date = models.DateField(auto_now_add=True)
    def clean(self):
        allowed_percentage= self.payslip.salary_contract.withdraw_allowed_percentage
        allowed_amount = self.payslip.base_monthly_salary * (allowed_percentage / 100)
        if self.amount > allowed_amount:
            raise ValidationError(f"your amount not allowed {allowed_amount}")
    def __str__(self):
        return f"withdrawal {self.amount} from your salary{self.payslip.id} في {self.date}"

