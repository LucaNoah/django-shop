import hashlib
from decimal import Decimal

from django.conf import settings

from products.models import ProductVariant

# Neuer Name, damit alte Warenkörbe (nur Produkt-IDs) nicht stören
SESSION_KEY = "bag_v2"


def calculate_delivery(total):
    """Versandkosten für einen Warenwert: gratis ab Schwelle oder bei 0."""
    if total == 0 or total >= settings.FREE_DELIVERY_THRESHOLD:
        return Decimal("0.00")
    return settings.STANDARD_DELIVERY_COST


def make_key(variant_id, personalization):
    """Eindeutiger Schlüssel einer Position aus Variante und Text, z. B. "12-3f9a1c0b7d"."""
    digest = hashlib.sha1(personalization.encode("utf-8")).hexdigest()[:10]
    return f"{variant_id}-{digest}"


class Bag:
    """Warenkorb eines Besuchers, gespeichert in seiner Session.

    In der Session steht je Position:
    {"12-3f9a1c0b7d": {"variant": 12, "personalization": "Für Anna", "quantity": 2}}
    Preise werden immer frisch aus der Datenbank gelesen.
    """

    def __init__(self, request):
        self.session = request.session
        self.lines = self.session.get(SESSION_KEY, {})

    def _save(self):
        self.session[SESSION_KEY] = self.lines
        self.session.modified = True

    def _reserved(self, variant_id, except_key=None):
        """Stück dieser Variante, die schon in anderen Positionen liegen."""
        return sum(
            line["quantity"]
            for key, line in self.lines.items()
            if line["variant"] == variant_id and key != except_key
        )

    def _set(self, key, variant, quantity, personalization):
        """Menge einer Position setzen, höchstens so viel wie noch auf Lager ist."""
        available = max(variant.stock - self._reserved(variant.id, except_key=key), 0)
        quantity = min(quantity, available)
        if quantity > 0:
            self.lines[key] = {
                "variant": variant.id,
                "personalization": personalization,
                "quantity": quantity,
            }
        else:
            self.lines.pop(key, None)
        self._save()
        return quantity

    def add(self, variant, quantity, personalization=""):
        """Variante hinzufügen. Gibt (gewünschte Menge, tatsächliche Menge) zurück."""
        key = make_key(variant.id, personalization)
        wanted = self.lines.get(key, {}).get("quantity", 0) + quantity
        actual = self._set(key, variant, wanted, personalization)
        return wanted, actual

    def update(self, key, quantity):
        """Menge einer Position ändern. Gibt (Variante, tatsächliche Menge) zurück."""
        line = self.lines.get(key)
        if line is None:
            return None, 0
        variant = (
            ProductVariant.objects.select_related("product")
            .filter(id=line["variant"])
            .first()
        )
        if variant is None:
            self.lines.pop(key, None)
            self._save()
            return None, 0
        actual = self._set(key, variant, quantity, line["personalization"])
        return variant, actual

    def remove(self, key):
        """Position entfernen. Gibt die Variante zurück (oder None)."""
        line = self.lines.pop(key, None)
        self._save()
        if line is None:
            return None
        return (
            ProductVariant.objects.select_related("product")
            .filter(id=line["variant"])
            .first()
        )

    def clear(self):
        """Warenkorb komplett leeren."""
        self.lines = {}
        self._save()

    def get_items(self):
        """Liste der Positionen mit Variante, Text, Menge und Preisen."""
        variant_ids = {line["variant"] for line in self.lines.values()}
        variants = ProductVariant.objects.filter(
            id__in=variant_ids, is_active=True, product__is_active=True
        ).select_related("product")
        by_id = {variant.id: variant for variant in variants}

        items = []
        for key, line in self.lines.items():
            variant = by_id.get(line["variant"])
            if variant is None:
                continue
            unit_price = variant.current_price
            items.append(
                {
                    "key": key,
                    "variant": variant,
                    "product": variant.product,
                    "personalization": line["personalization"],
                    "quantity": line["quantity"],
                    "unit_price": unit_price,
                    "subtotal": unit_price * line["quantity"],
                }
            )
        return items

    def get_summary(self):
        """Alle Zahlen des Warenkorbs auf einen Blick."""
        items = self.get_items()
        total = sum((item["subtotal"] for item in items), Decimal("0.00"))
        count = sum(item["quantity"] for item in items)
        delivery = calculate_delivery(total)

        return {
            "bag_items": items,
            "bag_count": count,
            "bag_total": total,
            "delivery": delivery,
            "free_delivery_missing": settings.FREE_DELIVERY_THRESHOLD - total,
            "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
            "grand_total": total + delivery,
        }
