import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation

logger = logging.getLogger(__name__)


def send_order_confirmation(order):
    """Bestellbestätigung in der Sprache der Bestellung schicken."""
    context = {"order": order}
    with translation.override(order.language):
        subject = render_to_string(
            "checkout/emails/confirmation_subject.txt", context
        ).strip()
        body = render_to_string("checkout/emails/confirmation_body.txt", context)
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.email])
    except Exception:
        # Die Zahlung ist trotzdem gültig, wir protokollieren nur den Fehler
        logger.exception("Bestätigungsmail für %s fehlgeschlagen", order.order_number)
