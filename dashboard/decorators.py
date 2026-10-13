from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def dashboard_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not request.user.is_staff:
            messages.error(request, "You do not have permission to access the dashboard.")
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not request.user.is_staff:
                raise PermissionDenied
            if not request.user.has_perm(permission):
                messages.error(request, "You do not have permission to perform this action.")
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator