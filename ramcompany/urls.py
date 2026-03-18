from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import unified_login ,about_me ,update_self


urlpatterns = [
    path('admin/', admin.site.urls),
    path('company/', include('companies.urls')),
    path('employee/', include('employees.urls')),
    path('salary/' , include('salaries.urls')),
    path('withdrawals/' , include('withdrawals.urls')),
    path('api/login/' , unified_login , name = "unified-login"),
    path('api/about/self/' , about_me ,name = "about-me"),
    path('api/update/self/', update_self ,name = "self-update")

]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
