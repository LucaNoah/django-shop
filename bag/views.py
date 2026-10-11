from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from products.models import Product

from .bag import Bag


def _get_quantity(request):
    """Menge aus dem Formular lesen, bei Unsinn 1."""
    try:
        return int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return 1


def bag_detail(request):
    """Warenkorb-Seite. Die Zahlen kommen aus dem Context Processor."""
    return render(request, "bag/bag_detail.html")


@require_POST
def bag_add(request, product_id):
    """Gewählte Ausführung (mit optionalem Text) in den Warenkorb legen."""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Gewählte Ausführung prüfen
    try:
        variant_id = int(request.POST.get("variant", ""))
    except ValueError:
        variant_id = None
    variant = None
    if variant_id:
        variant = product.variants.filter(id=variant_id, is_active=True).first()
    if variant is None:
        messages.error(request, _("This version is not available."))
        return redirect(product.get_absolute_url())

    back = f"{product.get_absolute_url()}?variant={variant.id}"

    # Personalisierung prüfen
    personalization = ""
    if product.personalization_enabled:
        personalization = (
            request.POST.get("personalization", "").replace("\r\n", "\n").strip()
        )
        if product.personalization_required and not personalization:
            messages.error(request, _("Please enter your personalization text."))
            return redirect(back)
        if len(personalization) > variant.personalization_max_length:
            messages.error(
                request,
                _("Your text is too long (maximum %(max)s characters).")
                % {"max": variant.personalization_max_length},
            )
            return redirect(back)

    if not variant.is_in_stock:
        messages.error(
            request, _("%(name)s is unfortunately sold out.") % {"name": variant}
        )
        return redirect(back)

    wanted, actual = Bag(request).add(
        variant, max(_get_quantity(request), 1), personalization
    )

    if actual < wanted:
        messages.warning(
            request,
            _("Only %(stock)s in stock. In your shopping bag: %(quantity)s.")
            % {"stock": variant.stock, "quantity": actual},
        )
    else:
        messages.success(
            request,
            _("%(name)s in your shopping bag: %(quantity)s.")
            % {"name": variant, "quantity": actual},
        )
    return redirect(back)


@require_POST
def bag_update(request, key):
    """Menge einer Position ändern. 0 entfernt sie."""
    wanted = _get_quantity(request)
    variant, actual = Bag(request).update(key, wanted)
    if variant is None:
        return redirect("bag:detail")

    if actual == 0:
        messages.success(
            request,
            _("%(name)s was removed from your shopping bag.") % {"name": variant},
        )
    elif actual < wanted:
        messages.warning(
            request,
            _("Only %(stock)s in stock. Quantity set to %(quantity)s.")
            % {"stock": variant.stock, "quantity": actual},
        )
    else:
        messages.success(
            request,
            _("Quantity of %(name)s changed to %(quantity)s.")
            % {"name": variant, "quantity": actual},
        )
    return redirect("bag:detail")


@require_POST
def bag_remove(request, key):
    """Position komplett aus dem Warenkorb nehmen."""
    variant = Bag(request).remove(key)
    if variant is not None:
        messages.success(
            request,
            _("%(name)s was removed from your shopping bag.") % {"name": variant},
        )
    return redirect("bag:detail")
