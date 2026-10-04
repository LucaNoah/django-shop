import stripe
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from products.models import Product

from .models import Order


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Meldungen von Stripe empfangen und prüfen."""
    payload = request.body
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError):
        # Ungültig oder nicht von Stripe
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        try:
            order_number = session["metadata"]["order_number"]
        except (KeyError, TypeError):
            order_number = None  # keine Bestellung von unserem Shop
        if order_number and session["payment_status"] == "paid":
            mark_order_paid(order_number)

    return HttpResponse(status=200)


def mark_order_paid(order_number):
    """Bestellung auf bezahlt setzen und Lager reduzieren, nur einmal."""
    with transaction.atomic():
        order = (
            Order.objects.select_for_update().filter(order_number=order_number).first()
        )
        if order is None or order.status != Order.Status.PENDING:
            return  # unbekannt oder schon erledigt

        for item in order.lineitems.all():
            Product.objects.filter(pk=item.product_id).update(
                stock=Greatest(F("stock") - item.quantity, 0)
            )

        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "paid_at"])
