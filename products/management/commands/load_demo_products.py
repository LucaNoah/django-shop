from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, Product, ProductVariant

CATEGORIES = {
    "bibelverse": ("Bibelverse", "Bible verses"),
    "motive": ("Christliche Motive", "Christian motifs"),
    "kunstobjekte": ("Kunstobjekte", "Art objects"),
}

DEDICATION = {
    "required": False,
    "label": ("Widmung (optional)", "Dedication (optional)"),
    "help": (
        "Wird auf der Rückseite eingraviert.",
        "Will be engraved on the back.",
    ),
    "max_length": 80,
}

# Varianten: (Name DE, Name EN, Preis, Sale-Preis, Lager)
# Leerer Name = Produkt hat nur eine Version (keine Auswahl im Shop)
PRODUCTS = [
    {
        "sku": "DEMO-001",
        "category": "bibelverse",
        "slug": "psalm-23-holzscheibe",
        "name": (
            "Psalm 23 auf Holzscheibe mit Rinde",
            "Psalm 23 on a wood slice with bark",
        ),
        "description": (
            "«Der Herr ist mein Hirte» – gelasert auf eine naturbelassene Holzscheibe mit Rinde.",
            "“The Lord is my shepherd” – laser engraved on a natural wood slice with bark.",
        ),
        "personalization": DEDICATION,
        "variants": [
            ("Ø 20 cm", "Ø 20 cm", "49.00", None, 8),
            ("Ø 30 cm", "Ø 30 cm", "79.00", None, 5),
            ("Ø 40 cm", "Ø 40 cm", "119.00", None, 2),
        ],
    },
    {
        "sku": "DEMO-002",
        "category": "bibelverse",
        "slug": "josua-1-9-sei-mutig",
        "name": (
            "Josua 1,9 – Sei mutig und stark",
            "Joshua 1:9 – Be strong and courageous",
        ),
        "description": (
            "Ein Zuspruch für jeden Tag, auf massivem Holz.",
            "Encouragement for every day, on solid wood.",
        ),
        "variants": [
            ("Eiche", "Oak", "69.00", None, 6),
            ("Nussbaum", "Walnut", "89.00", None, 3),
        ],
    },
    {
        "sku": "DEMO-003",
        "category": "bibelverse",
        "slug": "johannes-3-16",
        "name": ("Johannes 3,16", "John 3:16"),
        "description": (
            "Der bekannteste Vers der Bibel, schlicht und klar gestaltet.",
            "The best-known verse of the Bible, in a simple, clear design.",
        ),
        "variants": [
            ("", "", "59.00", "49.00", 10),
        ],
    },
    {
        "sku": "DEMO-004",
        "category": "bibelverse",
        "slug": "haussegen-familienname",
        "name": ("Haussegen mit Familienname", "House blessing with family name"),
        "description": (
            "«Der Herr segne dich und behüte dich» – mit eurem Familiennamen.",
            "“The Lord bless you and keep you” – with your family name.",
        ),
        "personalization": {
            "required": True,
            "label": ("Familienname", "Family name"),
            "help": ("Zum Beispiel: Familie Muster", "For example: The Smith Family"),
            "max_length": 40,
        },
        "variants": [
            ("", "", "89.00", None, 7),
        ],
    },
    {
        "sku": "DEMO-005",
        "category": "bibelverse",
        "slug": "taufschild-mit-name",
        "name": ("Taufschild mit Name und Datum", "Baptism sign with name and date"),
        "description": (
            "Ein bleibendes Geschenk zur Taufe.",
            "A lasting gift for a baptism.",
        ),
        "personalization": {
            "required": True,
            "label": ("Name und Taufdatum", "Name and baptism date"),
            "help": (
                "Zum Beispiel: Lea – 12. Mai 2027",
                "For example: Lea – 12 May 2027",
            ),
            "max_length": 50,
        },
        "variants": [
            ("Klein (15 × 20 cm)", "Small (15 × 20 cm)", "45.00", None, 10),
            ("Gross (25 × 35 cm)", "Large (25 × 35 cm)", "65.00", None, 4),
        ],
    },
    {
        "sku": "DEMO-006",
        "category": "bibelverse",
        "slug": "dreifache-schnur-hochzeit",
        "name": (
            "Prediger 4,12 – Dreifache Schnur",
            "Ecclesiastes 4:12 – A threefold cord",
        ),
        "description": (
            "Hochzeitsgeschenk mit den Namen des Paares und dem Hochzeitsdatum.",
            "Wedding gift with the couple's names and wedding date.",
        ),
        "personalization": {
            "required": True,
            "label": ("Namen und Datum", "Names and date"),
            "help": (
                "Zum Beispiel: Anna & David – 3. Juli 2027",
                "For example: Anna & David – 3 July 2027",
            ),
            "max_length": 60,
        },
        "variants": [
            ("", "", "129.00", None, 3),
        ],
    },
    {
        "sku": "DEMO-007",
        "category": "motive",
        "slug": "kreuz-wandobjekt",
        "name": ("Kreuz – Wandobjekt", "Cross – wall piece"),
        "description": (
            "Ein schlichtes Kreuz aus Massivholz zum Aufhängen.",
            "A simple solid wood cross to hang on the wall.",
        ),
        "variants": [
            ("", "", "39.00", None, 0),  # ausverkauft
        ],
    },
    {
        "sku": "DEMO-008",
        "category": "motive",
        "slug": "ichthys-fisch",
        "name": ("Ichthys – der Fisch", "Ichthys – the fish"),
        "description": (
            "Das älteste christliche Erkennungszeichen.",
            "The oldest Christian symbol of recognition.",
        ),
        "variants": [
            ("Natur", "Natural", "29.00", None, 12),
            ("Geölt", "Oiled", "34.00", None, 9),
        ],
    },
    {
        "sku": "DEMO-009",
        "category": "motive",
        "slug": "taube-mit-oelzweig",
        "name": ("Taube mit Ölzweig", "Dove with olive branch"),
        "description": (
            "Ein Zeichen für Frieden und Hoffnung.",
            "A sign of peace and hope.",
        ),
        "variants": [
            ("", "", "35.00", None, 6),
        ],
    },
    {
        "sku": "DEMO-010",
        "category": "kunstobjekte",
        "slug": "mehrschicht-kreuz-led",
        "name": ("Mehrschicht-Kreuz", "Multilayer cross"),
        "description": (
            "Mehrere Holzschichten ergeben ein Kreuz mit Tiefe – auf Wunsch mit LED-Licht.",
            "Several layers of wood form a cross with depth – optionally with LED light.",
        ),
        "variants": [
            ("Ohne LED", "Without LED", "149.00", None, 4),
            ("Mit LED", "With LED", "189.00", None, 2),
        ],
    },
    {
        "sku": "DEMO-011",
        "category": "kunstobjekte",
        "slug": "arche-noah-schichtbild",
        "name": ("Arche Noah – Schichtbild", "Noah's Ark – layered picture"),
        "description": (
            "Ein 3D-Bild aus mehreren Schichten, ideal fürs Kinderzimmer.",
            "A 3D picture made of several layers, ideal for a child's room.",
        ),
        "variants": [
            ("", "", "179.00", "159.00", 3),
        ],
    },
    {
        "sku": "DEMO-012",
        "category": "kunstobjekte",
        "slug": "lichtkreuz-tischleuchte",
        "name": ("Lichtkreuz – Tischleuchte", "Light cross – table lamp"),
        "description": (
            "Ein warm leuchtendes Kreuz für Tisch oder Regal.",
            "A warmly glowing cross for a table or shelf.",
        ),
        "variants": [
            ("", "", "99.00", None, 3),
        ],
    },
    {
        "sku": "DEMO-013",
        "category": "bibelverse",
        "slug": "seligpreisungen-entwurf",
        "name": ("Seligpreisungen (Entwurf)", "Beatitudes (draft)"),
        "description": (
            "Noch nicht sichtbar – zum Testen von «Aktiv».",
            "Not visible yet – for testing “active”.",
        ),
        "is_active": False,
        "variants": [
            ("", "", "99.00", None, 5),
        ],
    },
]


class Command(BaseCommand):
    help = "Creates or updates demo categories and products (SKU starts with DEMO-)."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name, (display_de, display_en) in CATEGORIES.items():
            category, _created = Category.objects.update_or_create(
                name=name,
                defaults={"display_name_de": display_de, "display_name_en": display_en},
            )
            categories[name] = category

        for data in PRODUCTS:
            pers = data.get("personalization")
            product, created = Product.objects.update_or_create(
                sku=data["sku"],
                defaults={
                    "category": categories[data["category"]],
                    "slug": data["slug"],
                    "name_de": data["name"][0],
                    "name_en": data["name"][1],
                    "description_de": data["description"][0],
                    "description_en": data["description"][1],
                    "is_active": data.get("is_active", True),
                    "personalization_enabled": pers is not None,
                    "personalization_required": bool(pers and pers["required"]),
                    "personalization_label_de": pers["label"][0] if pers else "",
                    "personalization_label_en": pers["label"][1] if pers else "",
                    "personalization_help_de": pers["help"][0] if pers else "",
                    "personalization_help_en": pers["help"][1] if pers else "",
                },
            )

            for position, (name_de, name_en, price, sale, stock) in enumerate(
                data["variants"]
            ):
                ProductVariant.objects.update_or_create(
                    sku=f"{data['sku']}-{position + 1}",
                    defaults={
                        "product": product,
                        "name_de": name_de,
                        "name_en": name_en,
                        "price": Decimal(price),
                        "sale_price": Decimal(sale) if sale else None,
                        "stock": stock,
                        "personalization_max_length": pers["max_length"]
                        if pers
                        else 100,
                        "position": position,
                        "is_active": True,
                    },
                )

            status = "created" if created else "updated"
            self.stdout.write(f"{status}: {data['sku']} {data['name'][0]}")

        self.stdout.write(self.style.SUCCESS(f"Done: {len(PRODUCTS)} demo products."))
