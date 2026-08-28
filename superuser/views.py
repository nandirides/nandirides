from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
# from superuser.forms import UserForm, LoginForm, profile
# from superuser.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

class SuperUserDashboardView(TemplateView):
    def get(self, request):
        return render(request, 'superuser/dashboard.html')
    