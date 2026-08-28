from django.urls import path
from superuser import views
urlpatterns = [
    
    path('', views.SuperUserDashboardView.as_view(), name='superuser-dashboard'),
]