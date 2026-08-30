from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from user.forms import UserForm, LoginForm, profile, ForgetPassword ,ResetPassword
from user.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User

BOOKING_OPTIONS = [
    {
        'icon': '🚕',
        'badge': 'Available Now',
        'badge_class': 'bg-success-subtle text-success',
        'title': 'Quick Booking',
        'description': (
            'Need a ride right now? Book your Nandi Ride '
            'instantly and reach your destination safely.'
        ),
        'features': [
            'Instant ride booking',
            'Fast driver matching',
            'Safe & reliable rides',
        ],
        'button_icon': '🚕',
        'button_text': 'Book Now',
        'url': 'booking',
        'button_class': 'btn-danger',
        'icon_bg': 'bg-danger bg-opacity-10',
        'icon_color': 'text-danger',
    },

    {
        'icon': '📋',
        'badge': 'Track Your Ride',
        'badge_class': 'bg-warning-subtle text-warning',
        'title': 'Booking Status',
        'description': (
            'Already booked a ride? Check your booking status '
            'using your registered mobile number or booking ID.'
        ),
        'features': [
            'Track booking status',
            'View ride details',
            'Check driver information',
        ],
        'button_icon': '📋',
        'button_text': 'Check Status',
        'url': 'booking-status',
        'button_class': 'btn-outline-danger',
        'icon_bg': 'bg-warning bg-opacity-10',
        'icon_color': 'text-warning',
    },
]

SIDEBAR_MENU = [
            {
                'icon': '🏠',
                'name': 'Dashboard',
                'url': 'user-dashboard',
            },
            {
                'icon': '👤',
                'name': 'Profile',
                'url': 'profile',
            },
            {
                'icon': '🛵',
                'name': 'My Rides',
                'url': 'myride',
            },
            {
                'icon': '📅',
                'name': 'Bookings',
                'url': 'booking',
            },
            {
                'icon': '💳',
                'name': 'Payments',
                'url': 'payment',
            },
        ]

SOCIAL_LINKS = [
        {
                'name': 'Google',
                'icon': 'fa-brands fa-google',
                'url': '#',
                'icon_bg': 'bg-opacity-10'
            },
            {
                'name': 'Facebook',
                'icon': 'fa-brands fa-facebook-f',
                'url': '#',
                'icon_bg': 'bg-success bg-opacity-10'
            },
            {
                'name': 'Instagram',
                'icon': 'fa-brands fa-instagram',
                'url': '#',
                'icon_bg': 'bg-danger bg-opacity-10'
            },
            {
                'name': 'LinkedIn',
                'icon': 'fa-brands fa-linkedin-in',
                'url': '#',
                'icon_bg': 'bg-primary bg-opacity-10'
            },
    ]

DASHBOARD_CARD = [
        {
                'name': 'Total Ride',
                'icon': 'fa-brands fa-road',
                'no': '15',
                'icon_bg': 'bg-primary bg-opacity-10'
            },
            {
                'name': 'Completed',
                'icon': 'fa-brands fa-check',
                'no': '25',
                'icon_bg': 'bg-success bg-opacity-10'
            },
            {
                'name': 'Cancelled',
                'icon': 'fa-brands fa-solid fa-xmark',
                'no': '19',
                'icon_bg': 'bg-danger bg-opacity-10'
            },
            {
                'name': 'Booking',
                'icon': 'fa-brands fa-taxi',
                'no': '13',
                'icon_bg': 'bg-primary bg-opacity-10'
            },
            {
                'name': 'Payment',
                'icon': 'fa-brands fa-money',
                'no': '1K',
                'icon_bg': 'bg-primary bg-opacity-10'
            },
    ]

class UserDashboardView(TemplateView):
    def get(self, request):
        return render(request, 'user/dashboard.html',{'sidebar_menu': SIDEBAR_MENU,'dashboard_card':DASHBOARD_CARD})

class UnderConstruction(TemplateView):
    def get(self, request):
        return render(request, 'user/underconstruction.html',)

class About(TemplateView):
    def get(self, request):
        return render(request, 'user/about.html',)

class Contact(TemplateView):
    def get(self, request):
        return render(request, 'user/contact.html',)

class UserHomeView(TemplateView):
    def get(self, request):
        return render(request, 'user/home.html',{
                'page_title': 'Book Your Ride',
                'page_subtitle': 'Quick, easy and reliable ride booking',
                'booking_options': BOOKING_OPTIONS,
            })

class UserBookingView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/booking.html',{'sidebar_menu': SIDEBAR_MENU})

class UserMyRideView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/myride.html',{'sidebar_menu': SIDEBAR_MENU})

class UserPaymentView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/payment.html',{'sidebar_menu': SIDEBAR_MENU})

class USerEditProfileView(TemplateView):
    def get(self, request):
        form = profile()
        return render(request, 'user/profile/editprofile.html', {'form': form,'sidebar_menu': SIDEBAR_MENU})
    
class UserLoginView(TemplateView):
    def get(self, request):
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form,'social_links': SOCIAL_LINKS,})

class UserSignupView(TemplateView):
    def get(self, request):
        form = UserForm()
        return render(request, 'user/signup.html', {'form': form,'social_links': SOCIAL_LINKS,})

class UserProfileView(TemplateView):
    def get(self, request):
        form = profile()
        return render(request, 'user/profile/profile.html', {'form': form, 'sidebar_menu': SIDEBAR_MENU,})

class ForgetPasswordView(TemplateView):
    def get(self, request):
        form = ForgetPassword()
        return render(request, 'user/profile/forgetpassword.html', {'form': form})

class ResetPasswordView(TemplateView):
    def get(self, request):
        form = ResetPassword()
        return render(request, 'user/profile/resetpassword.html', {'form': form})

# class UserLoginTypesView(TemplateView):
#     def get(self, request):
#         login_types = [
#             {
#                 'icon': '👤',
#                 'title': 'Public Login',
#                 'description': 'Login as a public user',
#                 'url': 'loginuser',
#                 'button_class': 'btn-primary',
#                 'border_class': 'border-primary',
#                 'button_text': 'Public Login',
#                 'signup': True,
#             },
#             {
#                 'icon': '🔐',
#                 'title': 'Admin Login',
#                 'description': 'Login to administration panel',
#                 'url': 'loginuser',
#                 'button_class': 'btn-dark',
#                 'border_class': 'border-dark',
#                 'button_text': 'Admin Login',
#                 'signup': False,
#             },
#         ]
#         return render(request,'user/logintype.html',{'login_types': login_types})

# class UserListView(TemplateView):
#     template_name = 'user/user_list.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         genre = self.request.GET.get('genre')
#         if genre:
#             context['users'] = User.objects.filter(genre=genre).order_by('-created_at')
#         else:
#             context['users'] = User.objects.all().order_by('-created_at')
#         return context