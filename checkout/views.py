import stripe
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from bag.bag import Bag
from profiles.models import UserProfile

from .forms import OrderForm
from .models import Order, OrderLineItem

stripe.api_key = settings.STRIPE_SECRET_KEY


def to_rappen(amount):
    """Stripe rechnet in der kleinsten Einheit: CHF 12.50 -> 1250."""
    return int(amount * 100)


def create_stripe_session(request, order):
    """Zahlungsseite bei Stripe für diese Bestellung anlegen."""
    line_items = [
        {
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {"name": item.product_name},
                "unit_amount": to_rappen(item.unit_price),
            },
            "quantity": item.quantity,
        }
        for item in order.lineitems.all()
    ]
    if order.delivery_cost > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {"name": _("Delivery")},
                    "unit_amount": to_rappen(order.delivery_cost),
                },
                "quantity": 1,
            }
        )

    success_url = request.build_absolute_uri(
        reverse("checkout:success", args=[order.order_number])
    )
    cancel_url = request.build_absolute_uri(reverse("bag:detail"))

    return stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        customer_email=order.email,
        client_reference_id=order.order_number,
        metadata={"order_number": order.order_number},
        success_url=success_url,
        cancel_url=cancel_url,
        locale=get_language() or "auto",
    )


def checkout(request):
    """Bestellformular anzeigen, Bestellung anlegen und zu Stripe weiterleiten."""
    bag = Bag(request)
    items = bag.get_items()
    if not items:
        messages.info(request, _("Your shopping bag is empty."))
        return redirect("products:product_list")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Reicht der Lagerbestand noch?
            for item in items:
                product = item["product"]
                if item["quantity"] > product.stock:
                    messages.error(
                        request,
                        _(
                            "Only %(stock)s of %(name)s are available. "
                            "Please adjust your shopping bag."
                        )
                        % {"stock": product.stock, "name": product.name},
                    )
                    return redirect("bag:detail")

            # Bestellung und Positionen zusammen speichern: alles oder nichts
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.language = get_language()  # NEU: Sprache der Bestellung merken
                order.save()
                for item in items:
                    OrderLineItem.objects.create(
                        order=order,
                        product=item["product"],
                        product_name=item["product"].name,
                        unit_price=item["product"].price,
                        quantity=item["quantity"],
                    )
                order.update_total()

            # Adresse im Profil speichern, wenn das Häkchen gesetzt ist
            if request.user.is_authenticated and request.POST.get("save_info"):
                profile, _created = UserProfile.objects.get_or_create(user=request.user)
                profile.default_full_name = order.full_name
                profile.default_phone_number = order.phone_number
                profile.default_street_address = order.street_address
                profile.default_postcode = order.postcode
                profile.default_town_or_city = order.town_or_city
                profile.default_country = order.country
                profile.save()

            # Zahlungsseite bei Stripe anlegen und dorthin weiterleiten
            try:
                session = create_stripe_session(request, order)
            except stripe.StripeError:
                messages.error(
                    request,
                    _(
                        "The payment could not be started right now. "
                        "Please try again later."
                    ),
                )
                return redirect("checkout:checkout")

            order.stripe_session_id = session.id
            order.save(update_fields=["stripe_session_id"])
            request.session["last_order_number"] = order.order_number
            return redirect(session.url, permanent=False)
    else:
        # Formular mit der gespeicherten Adresse vorausfüllen
        initial = {}
        if request.user.is_authenticated:
            profile, _created = UserProfile.objects.get_or_create(user=request.user)
            initial = {
                "full_name": profile.default_full_name,
                "email": request.user.email,
                "phone_number": profile.default_phone_number,
                "street_address": profile.default_street_address,
                "postcode": profile.default_postcode,
                "town_or_city": profile.default_town_or_city,
                "country": profile.default_country.code or "CH",
            }
        form = OrderForm(initial=initial)

    return render(request, "checkout/checkout.html", {"form": form})


def checkout_success(request, order_number):
    """Bestätigungsseite, nur für den Besteller sichtbar."""
    order = get_object_or_404(Order, order_number=order_number)
    from_this_session = request.session.get("last_order_number") == order_number
    is_owner = request.user.is_authenticated and order.user == request.user
    if not is_owner and not from_this_session:
        raise Http404

    # Zurück von Stripe: jetzt erst den Warenkorb leeren
    if from_this_session:
        Bag(request).clear()

    return render(request, "checkout/checkout_success.html", {"order": order})
