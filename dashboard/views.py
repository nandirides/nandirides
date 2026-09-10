from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserCreateForm, GalleryForm
from dashboard.models import Gallery

def ride_gallery(request):
    gallery = Gallery.objects.all()
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ride_gallery')
    else:
        form = GalleryForm()
    return render(request,'includes/gallery.html',{'form':form, 'gallery': gallery})




@login_required
def user_create(request, pk=None):
     # ADD USER
    if pk is None:
        user_obj = None
        page_title = "Add User"

    # UPDATE USER
    else:
        user_obj = get_object_or_404(
            User,
            pk=pk
        )
        page_title = "Edit User"

    if request.method == "POST":
        form = UserCreateForm(request.POST, instance = user_obj)

        if form.is_valid():
            user = form.save()
            if user_obj:
                messages.success(
                    request,
                    f"{user.username} updated successfully."
                )
            else:
                messages.success(
                    request,
                    f"{user.username} created successfully."
                )

            return redirect("user_list")
    else:
        
        form = UserCreateForm(
            instance = user_obj
        )

    return render(
        request,
        "dashboard/users/user_create.html",
        {
            "form": form,
            "user_obj": user_obj,
            "page_title": page_title,
        }
    )


@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(
            request,
            "You cannot delete your own account."
        )
        return redirect("user_list")

    else:
        request.method == "POST"
        username = user.username
        user.delete()

        messages.success(
            request,
            f"User '{username}' deleted successfully."
        )

        return redirect("user_list")

def gallery_delete(request, pk):
    data = get_object_or_404(Gallery, pk=pk)
    request.method == "POST"
    image = data.profile_image
    data.delete()

    messages.success(
        request,
        f"User '{image}' Image deleted successfully."
    )

    return redirect("ride_gallery")
    


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

# @login_required
# def ride_gallery(request):
#     return render(
#         request,
#         "includes/gallery.html",
#     )

@login_required
def user_list(request):
    users = User.objects.all()
    return render(
        request,
        "dashboard/users/list.html", {'users': users}
    )
