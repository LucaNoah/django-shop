from .bag import Bag


def bag_contents(request):
    """Stellt die Zahlen des Warenkorbs in jedem Template bereit."""
    return Bag(request).get_summary()
