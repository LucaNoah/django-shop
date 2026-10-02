# CLAUDE.md

## Projekt
Online-Shop mit Django. Zuerst Backend mit schlichtem Test-Frontend,
das Design macht später ein Designer. Neuaufbau meines Projekts
https://github.com/LucaNoah/gfeller-herbs (2023) mit aktuellen Versionen.

## Wichtig: Lernprojekt
- Ich lerne gerade wieder programmieren. Erkläre einfach, auf Deutsch.
- Schreibe Code nur, wenn ich ausdrücklich darum bitte. Sonst erklären,
  Hinweise geben, Fehler zeigen.
- Bei Fehlern: erst die Ursache erklären, dann die Lösung vorschlagen.
- Keine Datei ändern, ohne vorher zu sagen, was und warum.

## Technik
- Python 3.13, Django 5.2 LTS, PostgreSQL 17
- Läuft in Docker Compose: Service `web` (Django) und `db` (PostgreSQL)
- Django-Befehle immer im Container:
  `docker compose exec web python manage.py <befehl>`
- Einstellungen in `config/settings.py`, geheime Werte in `.env`
  (`.env` nie anzeigen, nie committen)
- Windows 11 + WSL2 (Ubuntu 26.04), Laptop mit 8 GB RAM:
  ressourcensparend arbeiten

## Konventionen
- Commits: `typ: zusammenfassung` + Stichpunkte, auf Englisch.
  Typen: feat, fix, chore, docs, style, refactor, test
- Frontend: nur schlichte Django-Templates, kein CSS-Framework
- Geschäftslogik gehört in Models oder eigene Funktionen,
  nicht in Templates (später kommt evtl. eine API dazu)