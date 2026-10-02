# Basis: schlankes Linux mit Python 3.13
FROM python:3.13-slim

# Python: keine .pyc-Dateien schreiben, Ausgaben sofort anzeigen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Benutzer mit derselben Nummer wie in Ubuntu (id -u = 1000),
# damit neu erzeugte Dateien dir gehören und nicht root
RUN useradd --create-home --uid 1000 app

WORKDIR /app

# Erst nur die Paketliste kopieren und installieren:
# so baut Docker diesen Teil nur neu, wenn sich die Liste ändert
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dann den restlichen Code kopieren
COPY --chown=app:app . .

USER app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]