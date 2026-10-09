from django import forms
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "default_full_name",
            "default_phone_number",
            "default_street_address",
            "default_postcode",
            "default_town_or_city",
            "default_country",
        ]
        labels = {
            "default_full_name": _("First and last name"),
            "default_phone_number": _("Phone"),
            "default_street_address": _("Street and house number"),
            "default_postcode": _("Postcode"),
            "default_town_or_city": _("Town or city"),
            "default_country": _("Country"),
        }
