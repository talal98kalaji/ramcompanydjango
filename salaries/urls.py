from django.urls import path
from . import views

app_name = 'salaries'

urlpatterns = [
    # --- 1. روابط خاصة بعقود الرواتب (SalaryContract) ---

    # [GET] لعرض قائمة بكل العقود
    # GET -> /api/salaries/contracts/
    path('contracts/', views.salary_contract_list, name='contract-list'),
    
    # [POST] لإنشاء عقد جديد
    # POST -> /api/salaries/contracts/create/
    path('contracts/create/', views.salary_contract_create, name='contract-create'),

    # [GET] لعرض تفاصيل عقد راتب معين
    # GET -> /api/salaries/contracts/1/
    path('contracts/<int:pk>/', views.salary_contract_detail, name='contract-detail'),
    
    # [PUT/PATCH] لتعديل عقد راتب معين
    # PUT/PATCH -> /api/salaries/contracts/1/update/
    path('contracts/<int:pk>/update/', views.salary_contract_update, name='contract-update'),


    # --- 2. روابط خاصة بكشوفات الرواتب الشهرية (MonthlyPayslip) ---

    # [GET] لعرض تفاصيل كشف راتب شهري معين
    # GET -> /api/salaries/payslips/123/ (حيث 123 هو ID كشف الراتب)
    path('payslips/<int:pk>/', views.monthly_payslip_detail, name='payslip-detail'),


    # --- 3. روابط خاصة بحركات الراتب (SalaryAdjustment) ---

    # [POST] لإضافة حركة (حسم أو مكافأة) على كشف راتب شهري معين
    # POST -> /api/salaries/payslips/123/add-adjustment/
    path('payslips/<int:payslip_pk>/add-adjustment/', views.add_salary_adjustment, name='add-adjustment'),
]

