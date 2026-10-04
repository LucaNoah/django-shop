from django.urls import path

from . import views, webhooks

app_name = "checkout"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("success/<str:order_number>/", views.checkout_success, name="success"),
    path("webhook/", webhooks.stripe_webhook, name="webhook"),
]
