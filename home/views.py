from django.shortcuts import render


def index(request):
    """Startseite des Shops."""
    return render(request, "home/index.html")