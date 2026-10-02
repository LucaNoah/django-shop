# django-shop

E-commerce store built with Django 5.2, PostgreSQL 17 and Docker.

## Run locally

1. Copy `.env.example` to `.env` and fill in the values
2. `docker compose up -d`
3. `docker compose exec web python manage.py migrate`
4. `docker compose exec web python manage.py createsuperuser`
5. Open http://localhost:8000