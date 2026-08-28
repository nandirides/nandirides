from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from user.forms import UserForm, LoginForm, profile, ForgetPassword ,ResetPassword
from user.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

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
            {
                'icon': '❤️',
                'name': 'Complaints',
                'url': 'complaints',
            },
            {
                'icon': '📞',
                'name': 'Support',
                'url': 'support',
            },
        ]

SOCIAL_LINKS = [
        {
            'name': 'Google',
            'icon': 'G',
            'url': '#',
        },
        {
            'name': 'Facebook',
            'icon': 'f',
            'url': '#',
        },
        {
            'name': 'Instagram',
            'icon': '◎',
            'url': '#',
        },
        {
            'name': 'LinkedIn',
            'icon': 'in',
            'url': '#',
        },
    ]

class UserDashboardView(TemplateView):
    def get(self, request):
        return render(request, 'user/dashboard.html',{'sidebar_menu': SIDEBAR_MENU})

class UserHomeView(TemplateView):
    def get(self, request):
        return render(request, 'user/home.html')

class UserBookingView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/booking.html')

class UserMyRideView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/myride.html')

class UserPaymentView(TemplateView):
    def get(self, request):
        return render(request, 'user/profile/payment.html')

class EditProfileView(TemplateView):
    def get(self, request):
        form = profile()
        return render(request, 'user/profile/editprofile.html', {'form': form})
    
class UserLoginView(TemplateView):
    def get(self, request):
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form})

class LogintypeView(TemplateView):
    def get(self, request): 
        return render(request, 'user/logintype.html')

class UserSignupView(TemplateView):
    def get(self, request):
        form = UserForm()
        return render(request, 'user/signup.html', {'form': form})

class UserProfileView(TemplateView):
    def get(self, request):
        form = profile()
        return render(request, 'user/profile/profile.html', {'form': form})

class ForgetPasswordView(TemplateView):
    def get(self, request):
        form = ForgetPassword()
        return render(request, 'user/profile/forgetpassword.html', {'form': form})

class ResetPasswordView(TemplateView):
    def get(self, request):
        form = ResetPassword()
        return render(request, 'user/profile/resetpassword.html', {'form': form})

class UserLoginTypesView(TemplateView):
    def get(self, request):
        login_types = [
            {
                'icon': '👤',
                'title': 'Public Login',
                'description': 'Login as a public user',
                'url': 'loginuser',
                'button_class': 'btn-primary',
                'border_class': 'border-primary',
                'button_text': 'Public Login',
                'signup': True,
            },
            {
                'icon': '🔐',
                'title': 'Admin Login',
                'description': 'Login to administration panel',
                'url': 'loginuser',
                'button_class': 'btn-dark',
                'border_class': 'border-dark',
                'button_text': 'Admin Login',
                'signup': False,
            },
        ]
        return render(request,'user/logintype.html',{'login_types': login_types})

class UserSignupView(TemplateView):
    def get(self, request):
        form = UserForm()
        return render(request,'user/signup.html',{'form': form,'social_links': SOCIAL_LINKS,}
        )

class UserLoginView(TemplateView):
    def get(self, request):
        form = LoginForm()
        return render(request,'user/login.html',{'form': form,'social_links': SOCIAL_LINKS}
        )
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