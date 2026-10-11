from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Produktkategorie, z. B. Bibelverse oder Kunstobjekte."""

    name = models.CharField(_("internal name"), max_length=100, unique=True)
    display_name = models.CharField(_("display name"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self):
        return self.display_name or self.name


class Product(models.Model):
    """Ein Produkt im Shop. Preis und Lager stehen bei den Varianten."""

    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    sku = models.CharField(_("item number"), max_length=30, blank=True)
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("URL name"), max_length=200, unique=True)
    description = models.TextField(_("description"))
    image = models.ImageField(_("main image"), upload_to="products/", blank=True)
    is_active = models.BooleanField(
        _("active"), default=True, help_text=_("Visible in the shop")
    )

    # Personalisierung (eigener Text des Kunden, z. B. Bibelvers oder Widmung)
    personalization_enabled = models.BooleanField(
        _("personalization possible"), default=False
    )
    personalization_required = models.BooleanField(
        _("personalization required"), default=False
    )
    personalization_label = models.CharField(
        _("label of the text field"), max_length=100, blank=True
    )
    personalization_help = models.CharField(
        _("hint below the text field"), max_length=200, blank=True
    )

    # Für Suchmaschinen (Ausgabe folgt in Phase 14)
    meta_title = models.CharField(_("meta title"), max_length=70, blank=True)
    meta_description = models.CharField(
        _("meta description"), max_length=160, blank=True
    )

    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])

    @property
    def active_variants(self):
        """Alle Varianten, die im Shop angeboten werden."""
        return [variant for variant in self.variants.all() if variant.is_active]

    @property
    def price_from(self):
        """Tiefster aktueller Preis aller Varianten."""
        prices = [variant.current_price for variant in self.active_variants]
        return min(prices) if prices else None

    @property
    def has_price_range(self):
        """True, wenn die Varianten unterschiedlich viel kosten."""
        return len({variant.current_price for variant in self.active_variants}) > 1

    @property
    def is_available(self):
        """True, wenn mindestens eine Variante auf Lager ist."""
        return any(variant.is_in_stock for variant in self.active_variants)

    @property
    def is_on_sale(self):
        """True, wenn mindestens eine Variante einen Sale-Preis hat."""
        return any(variant.is_on_sale for variant in self.active_variants)

    @property
    def cover_image(self):
        """Bild für Listen: Hauptbild, sonst das erste Galeriebild."""
        if self.image:
            return self.image
        first = next(iter(self.images.all()), None)
        return first.image if first else None


class ProductVariant(models.Model):
    """Eine kaufbare Ausführung eines Produkts, z. B. „30 × 20 cm, geölt“.

    Produkte ohne Auswahl haben genau eine Variante ohne Namen.
    """

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(
        _("name"),
        max_length=100,
        blank=True,
        help_text=_("Leave empty if the product has only one version."),
    )
    sku = models.CharField(_("item number"), max_length=30, blank=True)
    price = models.DecimalField(_("price"), max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(
        _("sale price"), max_digits=8, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField(_("stock"), default=0)
    personalization_max_length = models.PositiveSmallIntegerField(
        _("max. characters"),
        default=100,
        help_text=_("Only relevant if personalization is possible."),
    )
    position = models.PositiveIntegerField(_("position"), default=0)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("version")
        verbose_name_plural = _("versions")
        ordering = ["position", "id"]

    def __str__(self):
        if self.name:
            return f"{self.product.name} – {self.name}"
        return self.product.name

    @property
    def is_on_sale(self):
        """True, wenn ein tieferer Sale-Preis gesetzt ist."""
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def current_price(self):
        """Der Preis, den der Kunde bezahlt."""
        return self.sale_price if self.is_on_sale else self.price

    @property
    def is_in_stock(self):
        """True, wenn mindestens ein Stück auf Lager ist."""
        return self.stock > 0


class ProductImage(models.Model):
    """Galeriebild eines Produkts.

    Ohne Variante gilt das Bild für alle Ausführungen,
    mit Variante nur für diese.
    """

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="images",
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_("version"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="images",
        help_text=_("Empty = for all versions."),
    )
    image = models.ImageField(_("image"), upload_to="products/gallery/")
    alt_text = models.CharField(_("alternative text"), max_length=200, blank=True)
    position = models.PositiveIntegerField(_("position"), default=0)

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["position", "id"]

    def __str__(self):
        return f"Bild {self.position} von {self.product}"
