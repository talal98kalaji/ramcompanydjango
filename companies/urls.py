from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_company, name='company-register'),
    path('all/', views.list_companies, name='company-list'),
    path('<int:company_id>/', views.get_company_by_id, name='company-detail'),
    path('profile/update/', views.update_company, name='company-update'),
    path('delete/<int:pk>/', views.delete_company_profile, name='company-delete'),
    path('change-password/' , views.change_password , name = "change-password")
]

