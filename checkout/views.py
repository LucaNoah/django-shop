from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from bag.bag import Bag
from profiles.models import UserProfile

from .forms import OrderForm
from .models import Order, OrderLineItem


def checkout(request):
    """Bestellformular anzeigen und Bestellung anlegen."""
    bag = Bag(request)
    items = bag.get_items()
    if not items:
        messages.info(request, "Dein Warenkorb ist leer.")
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
                        f"Von {product.name} sind nur noch {product.stock} Stück "
                        f"verfügbar. Bitte passe deinen Warenkorb an.",
                    )
                    return redirect("bag:detail")

            # Bestellung und Positionen zusammen speichern: alles oder nichts
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
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

            bag.clear()

            # Adresse im Profil speichern, wenn das Häkchen gesetzt ist
            if request.user.is_authenticated and request.POST.get("save_info"):
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.default_full_name = order.full_name
                profile.default_phone_number = order.phone_number
                profile.default_street_address = order.street_address
                profile.default_postcode = order.postcode
                profile.default_town_or_city = order.town_or_city
                profile.default_country = order.country
                profile.save()

            request.session["last_order_number"] = order.order_number
            return redirect("checkout:success", order_number=order.order_number)
    else:
        # Formular mit der gespeicherten Adresse vorausfüllen
        initial = {}
        if request.user.is_authenticated:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
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
    is_owner = request.user.is_authenticated and order.user == request.user
    if not is_owner and request.session.get("last_order_number") != order_number:
        raise Http404
    return render(request, "checkout/checkout_success.html", {"order": order})
