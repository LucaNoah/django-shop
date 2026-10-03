from django import forms

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
            "default_full_name": "Vor- und Nachname",
            "default_phone_number": "Telefon",
            "default_street_address": "Strasse und Hausnummer",
            "default_postcode": "PLZ",
            "default_town_or_city": "Ort",
            "default_country": "Land",
        }
