from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from checkout.webhooks import stripe_webhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("checkout/webhook/", stripe_webhook, name="stripe_webhook"),
]

urlpatterns += i18n_patterns(
    path("accounts/", include("allauth.urls")),
    path("products/", include("products.urls")),
    path("bag/", include("bag.urls")),
    path("checkout/", include("checkout.urls")),
    path("profile/", include("profiles.urls")),
    path("", include("home.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
