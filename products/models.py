from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Produktkategorie, z. B. Bibelverse oder Kunstobjekte."""

    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.display_name or self.name


class Product(models.Model):
    """Ein Produkt im Shop. Preis und Lager stehen bei den Varianten."""

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    sku = models.CharField("SKU", max_length=30, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    # Alte Felder, werden in Schritt 9.4 entfernt
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)

    # Personalisierung (eigener Text des Kunden, z. B. Bibelvers oder Widmung)
    personalization_enabled = models.BooleanField(default=False)
    personalization_label = models.CharField(max_length=100, blank=True)
    personalization_help = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])

    @property
    def is_in_stock(self):
        """True, wenn mindestens ein Stück auf Lager ist."""
        return self.stock > 0


class ProductVariant(models.Model):
    """Eine kaufbare Ausführung eines Produkts, z. B. „30 × 20 cm, geölt“.

    Produkte ohne Auswahl haben genau eine Variante ohne Namen.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(max_length=100, blank=True)
    sku = models.CharField("SKU", max_length=30, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField(default=0)
    personalization_max_length = models.PositiveSmallIntegerField(default=100)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
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
        on_delete=models.CASCADE,
        related_name="images",
    )
    variant = models.ForeignKey(
        ProductVariant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"Bild {self.position} von {self.product}"
