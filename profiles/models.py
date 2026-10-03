from django.conf import settings
from django.db import models
from django_countries.fields import CountryField


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    default_full_name = models.CharField(max_length=100, blank=True)
    default_phone_number = models.CharField(max_length=30, blank=True)
    default_street_address = models.CharField(max_length=200, blank=True)
    default_postcode = models.CharField(max_length=20, blank=True)
    default_town_or_city = models.CharField(max_length=100, blank=True)
    default_country = CountryField(blank=True, default="CH")

    def __str__(self):
        return f"Profil von {self.user.email}"
