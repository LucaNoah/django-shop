from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import UserProfileForm
from .models import UserProfile


@login_required
def profile(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your address has been saved."))
            return redirect("profiles:profile")
        messages.error(request, _("Please check the highlighted fields."))
    else:
        form = UserProfileForm(instance=profile)

    orders = request.user.orders.order_by("-created_at")
    return render(request, "profiles/profile.html", {"form": form, "orders": orders})
