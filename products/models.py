from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Produktkategorie, z. B. Tee oder Öl."""

    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.display_name or self.name


class Product(models.Model):
    """Ein Produkt im Shop."""

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    sku = models.CharField("SKU", max_length=30, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)  # NEU
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # NEU
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        """True, wenn mindestens ein Stück auf Lager ist."""
        return self.stock > 0

    def get_absolute_url(self):
        """Adresse der Detailseite dieses Produkts."""
        return reverse("products:product_detail", args=[self.slug])


class ProductImage(models.Model):
    """Zusätzliches Bild für die Galerie eines Produkts."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"Bild {self.position} von {self.product}"
