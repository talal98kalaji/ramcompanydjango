from django.urls import path
from . import views

app_name = 'salaries'

urlpatterns = [
    #GET Shows All Contracts
    #/api/salaries/contracts/
    path('contracts/', views.salary_contract_list, name='contract-list'),
    
    #POST Create new contract
    #/api/salaries/contracts/create/
    path('contracts/create/', views.salary_contract_create, name='contract-create'),

    #GET Detail of Contract id
    #/api/salaries/contracts/1/
    path('contracts/<int:pk>/', views.salary_contract_detail, name='contract-detail'),
    
    #PUT/PATCH Edit one Contract by ID
    #/api/salaries/contracts/1/update/
    path('contracts/<int:pk>/update/', views.salary_contract_update, name='contract-update'),

    #(MonthlyPayslip)   
    #/api/salaries/payslips/123/ 
    path('payslips/<int:pk>/', views.monthly_payslip_detail, name='payslip-detail'),
    #/api/salaries/payslips/123/add-adjustment/
    path('payslips/<int:payslip_pk>/add-adjustment/', views.add_salary_adjustment, name='add-adjustment'),
]

