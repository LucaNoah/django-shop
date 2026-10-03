from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "default_full_name",
        "default_town_or_city",
        "default_country",
    ]
    search_fields = ["user__email", "default_full_name"]
