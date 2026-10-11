from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

GROUP_NAME = "Shop-Betreiber"

# App -> Model -> erlaubte Aktionen
PERMISSIONS = {
    "products": {
        "category": ["add", "change", "delete", "view"],
        "product": ["add", "change", "delete", "view"],
        "productvariant": ["add", "change", "delete", "view"],
        "productimage": ["add", "change", "delete", "view"],
    },
    "checkout": {
        "order": ["change", "view"],
        "orderlineitem": ["change", "view"],
    },
}


class Command(BaseCommand):
    help = "Legt die Gruppe „Shop-Betreiber“ mit passenden Rechten an (mehrfach ausführbar)."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name=GROUP_NAME)

        permissions = []
        for app_label, models in PERMISSIONS.items():
            for model, actions in models.items():
                for action in actions:
                    permissions.append(
                        Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=f"{action}_{model}",
                        )
                    )

        group.permissions.set(permissions)

        status = "angelegt" if created else "aktualisiert"
        self.stdout.write(
            self.style.SUCCESS(
                f"Gruppe „{GROUP_NAME}“ {status}, {len(permissions)} Rechte vergeben."
            )
        )
