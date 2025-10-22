from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.register_employee , name = 'sign-up-user'),
    path('<int:employee_id>/get/' , views.get_employee_by_id , name = 'get-by-id'),
    path('getall/' , views.get_all_employees , name = 'get-all-employees'),
    path('<int:employee_id>/update/' , views.update_employee , name = 'edit-employee'),
    path('get/name/' , views.get_employee_by_name , name = 'get-employee-by-name'),
    path('<int:employee_id>/delete/' , views.delete_employee , name = 'delete-employee'),
    path('change-password/' , views.change_password , name = 'change-password'),
    #requests
    path('request/pending/' , views.list_pending_requests , name = 'pending-requests'),
    path('request/<int:pk>/accept/' , views.accept_employment_request , name = 'accept-request'),
    path('request/<int:pk>/reject/' , views.reject_employment_request , name = 'reject-request'),
    path('request/creat/' ,  views.create_employment_request , name = "only-request-company")

]