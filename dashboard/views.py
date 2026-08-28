from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
    )


@login_required
def user_list(request):
    return render(
        request,
        "dashboard/users/list.html",
    )


@login_required
def user_create(request):
    return render(
        request,
        "dashboard/users/create.html",
    )