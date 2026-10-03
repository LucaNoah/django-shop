from decimal import Decimal

from django.conf import settings

from products.models import Product

SESSION_KEY = "bag"


class Bag:
    """Warenkorb eines Besuchers, gespeichert in seiner Session.

    In der Session steht nur {Produkt-ID: Menge}, z. B. {"3": 2}.
    Preise werden immer frisch aus der Datenbank gelesen.
    """

    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(SESSION_KEY, {})

    def _save(self):
        self.session[SESSION_KEY] = self.items

    def get_quantity(self, product):
        """Menge eines Produkts im Warenkorb (0, wenn nicht drin)."""
        return self.items.get(str(product.id), 0)

    def set_quantity(self, product, quantity):
        """Menge setzen. 0 oder weniger entfernt das Produkt.

        Mehr als der Lagerbestand ist nicht möglich.
        """
        key = str(product.id)
        quantity = min(quantity, product.stock)
        if quantity > 0:
            self.items[key] = quantity
        else:
            self.items.pop(key, None)
        self._save()

    def remove(self, product):
        """Produkt komplett aus dem Warenkorb nehmen."""
        self.items.pop(str(product.id), None)
        self._save()

    def get_items(self):
        """Liste der Positionen mit Produkt, Menge und Zwischensumme."""
        products = Product.objects.filter(id__in=self.items.keys(), is_active=True)
        return [
            {
                "product": product,
                "quantity": self.items[str(product.id)],
                "subtotal": product.price * self.items[str(product.id)],
            }
            for product in products
        ]

    def get_summary(self):
        """Alle Zahlen des Warenkorbs auf einen Blick."""
        items = self.get_items()
        total = sum((item["subtotal"] for item in items), Decimal("0.00"))
        count = sum(item["quantity"] for item in items)

        if total == 0 or total >= settings.FREE_DELIVERY_THRESHOLD:
            delivery = Decimal("0.00")
        else:
            delivery = settings.STANDARD_DELIVERY_COST

        return {
            "bag_items": items,
            "bag_count": count,
            "bag_total": total,
            "delivery": delivery,
            "free_delivery_missing": settings.FREE_DELIVERY_THRESHOLD - total,
            "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
            "grand_total": total + delivery,
        }
