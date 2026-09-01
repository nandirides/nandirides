from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
    )

@login_required
def user_profile(request):
    return render(
        request,
        "account/profile.html",
    )

@login_required
def user_setting(request):
    return render(
        request,
        "account/setting.html",
    )

@login_required
def user_ridestatus(request):
    return render(
        request,
        "dashboard/users/ridestatus.html",
    )

@login_required
def ride_gallery(request):
    return render(
        request,
        "includes/gallery.html",
    )

@login_required
def user_list(request):
    from django.contrib.auth.models import User
    users = User.objects.all()
    return render(
        request,
        "dashboard/users/list.html", {'users': users}
    )


@login_required
def user_create(request):
    return render(
        request,
        "dashboard/users/create.html",
    )