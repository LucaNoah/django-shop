from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order


class OrderForm(forms.ModelForm):
    """Formular für Kontaktdaten und Lieferadresse."""

    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone_number",
            "street_address",
            "postcode",
            "town_or_city",
            "country",
        ]
        labels = {
            "full_name": _("First and last name"),
            "email": _("Email"),
            "phone_number": _("Phone (optional)"),
            "street_address": _("Street and house number"),
            "postcode": _("Postcode"),
            "town_or_city": _("Town or city"),
            "country": _("Country"),
        }
