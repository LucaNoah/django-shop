from django import forms

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
            "full_name": "Vor- und Nachname",
            "email": "E-Mail",
            "phone_number": "Telefon (optional)",
            "street_address": "Strasse und Hausnummer",
            "postcode": "PLZ",
            "town_or_city": "Ort",
            "country": "Land",
        }
