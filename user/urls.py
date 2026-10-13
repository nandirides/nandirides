from django.urls import path
from django.contrib.auth import views as auth_views
from user import views
urlpatterns = [
    
    path('', views.HomeView.as_view(), name='home'),
    path('cancel-ride/', views.CancelRideView.as_view(), name='cancel-ride'),
    path('booking/', views.UserBookingView.as_view(), name='booking'),
    path('payment/', views.UserPaymentView.as_view(), name='payment'),
    path('myride/', views.UserMyRideView.as_view(), name='myride'),
    path('user/dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('editprofile/', views.UserEditProfileView.as_view(), name='editprofile'),
    path('user/signup/', views.UserSignupView.as_view(), name='user-signup'),
    path('user/login/', views.UserLoginView.as_view(), name='user-login'),
    path("user/logout/",auth_views.LogoutView.as_view(next_page="user-login"),name="logoutUser"),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('forgetpassword/', views.ForgetPasswordView.as_view(), name='forgetpassword'),
    path('resetpassword/', views.ResetPasswordView.as_view(), name='resetpassword'),
    path('underconstruction/', views.UnderConstruction.as_view(), name='underconstruction'),
    path('user/about/', views.About.as_view(), name='user-about'),
    path('user/contact/', views.ContactView.as_view(), name='user-contact'),
    path('track/', views.TrackRideView.as_view(), name='track'),
    path('user/career/', views.CareerView.as_view(), name='user-career'),
    path('user/blog/', views.BlogView.as_view(), name='user-blog'),
    #path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('user/services/', views.ServicesView.as_view(), name='user-services'),
    path('paymentdetails/', views.PaymentDetailsView.as_view(), name='paymentdetails'),
    path('paymentreceipt/', views.PaymentReceiptView.as_view(), name='paymentreceipt'),
    path('help-chatbot/', views.HelpChatbotView.as_view(), name='help-chatbot'),
    # path('', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.usersDetailView.as_view(), name='users-detail'),
    # path('users/new/', views.usersCreateView.as_view(), name='users-create'),
    # path('users/<int:pk>/edit/', views.usersUpdateView.as_view(), name='users-update'),
    # path('users/<int:pk>/delete/', views.usersDeleteView.as_view(), name='users-delete'),
   
    
]