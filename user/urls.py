from django.urls import path
from user import views
urlpatterns = [
    
    path('', views.UserHomeView.as_view(), name='home'),
    path('booking/', views.UserBookingView.as_view(), name='booking'),
    path('payment/', views.UserPaymentView.as_view(), name='payment'),
    path('myride/', views.UserMyRideView.as_view(), name='myride'),
    path('userdashboard', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('editprofile/', views.USerEditProfileView.as_view(), name='editprofile'),
    #path('login/', views.UserLoginTypesView.as_view(), name='login'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    # path('', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.usersDetailView.as_view(), name='users-detail'),
    # path('users/new/', views.usersCreateView.as_view(), name='users-create'),
    # path('users/<int:pk>/edit/', views.usersUpdateView.as_view(), name='users-update'),
    # path('users/<int:pk>/delete/', views.usersDeleteView.as_view(), name='users-delete'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('forgetpassword/', views.ForgetPasswordView.as_view(), name='forgetpassword'),
    path('resetpassword/', views.ResetPasswordView.as_view(), name='resetpassword'),
    #path('logintypes/', views.UserLoginTypesView.as_view(), name='logintypes'),
    path('underconstruction/', views.UnderConstruction.as_view(), name='underconstruction'),
    path('about/', views.About.as_view(), name='about'),
    path('contact/', views.Contact.as_view(), name='contact'),
]