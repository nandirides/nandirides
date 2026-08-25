from django.urls import path
from user import views
urlpatterns = [
    
    path('', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    # path('', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.usersDetailView.as_view(), name='users-detail'),
    # path('users/new/', views.usersCreateView.as_view(), name='users-create'),
    # path('users/<int:pk>/edit/', views.usersUpdateView.as_view(), name='users-update'),
    # path('users/<int:pk>/delete/', views.usersDeleteView.as_view(), name='users-delete'),
]