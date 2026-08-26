from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from user.forms import UserForm, LoginForm, profile
# from user.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

class UserDashboardView(TemplateView):
    def get(self, request):
        return render(request, 'user/dashboard.html')
    
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