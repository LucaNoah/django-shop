import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from bag.bag import calculate_delivery
from products.models import Product


class Order(models.Model):
    """Eine Bestellung mit Lieferadresse und Beträgen."""

    class Status(models.TextChoices):
        PENDING = "pending", "Offen"
        PAID = "paid", "Bezahlt"
        SHIPPED = "shipped", "Versendet"
        CANCELLED = "cancelled", "Storniert"

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30, blank=True)
    street_address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=20)
    town_or_city = models.CharField(max_length=100)
    country = CountryField(default="CH")

    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    stripe_session_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        """Beim ersten Speichern eine zufällige Bestellnummer vergeben."""
        if not self.order_number:
            self.order_number = uuid.uuid4().hex.upper()
        super().save(*args, **kwargs)

    def update_total(self):
        """Summen aus den Positionen neu berechnen und speichern."""
        self.order_total = sum(
            (item.lineitem_total for item in self.lineitems.all()), Decimal("0.00")
        )
        self.delivery_cost = calculate_delivery(self.order_total)
        self.grand_total = self.order_total + self.delivery_cost
        self.save()


class OrderLineItem(models.Model):
    """Eine Position einer Bestellung, mit Preis zum Kaufzeitpunkt."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lineitems")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    product_name = models.CharField(max_length=200, blank=True)
    unit_price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    quantity = models.PositiveIntegerField()
    lineitem_total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )

    def save(self, *args, **kwargs):
        """Leere Felder vom Produkt übernehmen, Positionssumme berechnen."""
        if not self.product_name:
            self.product_name = self.product.name
        if self.unit_price is None:
            self.unit_price = self.product.price
        self.lineitem_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"
