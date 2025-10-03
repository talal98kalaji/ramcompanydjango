from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_withdrawal , name = "create-withdrawal" ),
    path('' , views.get_all_withdrawals , name = "get-all-withdrawals"),
    path('get/detail/' ,views.get_withdrawal_summery , name= "get-all-details")
]
