from django.urls import path
from user import views
urlpatterns = [
    
    path('', views.HomeView.as_view(), name='home'),
    path('cancel-ride/', views.CancelRideView.as_view(), name='cancel-ride'),
    path('booking/', views.UserBookingView.as_view(), name='booking'),
    path('payment/', views.UserPaymentView.as_view(), name='payment'),
    path('myride/', views.UserMyRideView.as_view(), name='myride'),
    path('dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('editprofile/', views.UserEditProfileView.as_view(), name='editprofile'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('forgetpassword/', views.ForgetPasswordView.as_view(), name='forgetpassword'),
    path('resetpassword/', views.ResetPasswordView.as_view(), name='resetpassword'),
    path('underconstruction/', views.UnderConstruction.as_view(), name='underconstruction'),
    path('about/', views.About.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('track/', views.TrackRideView.as_view(), name='track'),
    path('career/', views.CareerView.as_view(), name='career'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    #path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('paymentdetails/', views.PaymentDetailsView.as_view(), name='paymentdetails'),
    path('paymentreceipt/', views.PaymentReceiptView.as_view(), name='paymentreceipt'),
    # path('', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.usersDetailView.as_view(), name='users-detail'),
    # path('users/new/', views.usersCreateView.as_view(), name='users-create'),
    # path('users/<int:pk>/edit/', views.usersUpdateView.as_view(), name='users-update'),
    # path('users/<int:pk>/delete/', views.usersDeleteView.as_view(), name='users-delete'),
   
    
]