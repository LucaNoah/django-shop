import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from bag.bag import calculate_delivery
from products.models import Product, ProductVariant


class Order(models.Model):
    """Eine Bestellung mit Lieferadresse und Beträgen."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        SHIPPED = "shipped", _("Shipped")
        CANCELLED = "cancelled", _("Cancelled")

    order_number = models.CharField(
        _("order number"), max_length=32, unique=True, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("customer account"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.PENDING
    )

    full_name = models.CharField(_("full name"), max_length=100)
    email = models.EmailField(_("email"))
    phone_number = models.CharField(_("phone"), max_length=30, blank=True)
    street_address = models.CharField(_("street and house number"), max_length=200)
    postcode = models.CharField(_("postcode"), max_length=20)
    town_or_city = models.CharField(_("town or city"), max_length=100)
    country = CountryField(_("country"), default="CH")

    order_total = models.DecimalField(
        _("items total"), max_digits=10, decimal_places=2, default=0
    )
    delivery_cost = models.DecimalField(
        _("delivery"), max_digits=8, decimal_places=2, default=0
    )
    grand_total = models.DecimalField(
        _("total"), max_digits=10, decimal_places=2, default=0
    )

    stripe_session_id = models.CharField(
        _("Stripe session"), max_length=255, blank=True
    )
    paid_at = models.DateTimeField(_("paid at"), null=True, blank=True)
    language = models.CharField(_("language"), max_length=10, default="de")

    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
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
    """Eine Position einer Bestellung, mit Namen und Preis zum Kaufzeitpunkt."""

    order = models.ForeignKey(
        Order,
        verbose_name=_("order"),
        on_delete=models.CASCADE,
        related_name="lineitems",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_("version"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_name = models.CharField(_("product name"), max_length=200, blank=True)
    variant_name = models.CharField(_("version name"), max_length=100, blank=True)
    personalization = models.TextField(_("personalization text"), blank=True)
    unit_price = models.DecimalField(
        _("unit price"), max_digits=8, decimal_places=2, blank=True, null=True
    )
    quantity = models.PositiveIntegerField(_("quantity"))
    lineitem_total = models.DecimalField(
        _("total"), max_digits=10, decimal_places=2, editable=False
    )

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def save(self, *args, **kwargs):
        """Leere Felder aus Produkt und Variante übernehmen, Summe berechnen."""
        if not self.product_name:
            self.product_name = self.product.name
        if self.variant:
            if not self.variant_name:
                self.variant_name = self.variant.name
            if self.unit_price is None:
                self.unit_price = self.variant.current_price
        self.lineitem_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Name für Anzeige, Stripe und Mail, z. B. „Psalm 23 – 30 × 20 cm, geölt“."""
        if self.variant_name:
            return f"{self.product_name} – {self.variant_name}"
        return self.product_name

    def __str__(self):
        return f"{self.quantity} × {self.display_name}"
