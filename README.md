# Hearth and Crumb

Hearth and Crumb is a small-batch bakery storefront built with Django 5.1. It provides a product catalog with categories, search and featured items, a session based basket, a checkout flow that reserves stock inside a database transaction, order tracking for customers, a contact form, and a staff back office in the Django admin for managing products, categories, orders and incoming messages.

## Features

- Catalog with categories, search, product detail pages and related products
- Session basket with stock limits, quantity updates and removal
- Checkout with pickup time validation and atomic stock reservation
- Order reference lookup for customers
- Contact form with honeypot spam protection
- Admin actions to move orders through their lifecycle
- Management command that loads the demo catalog
- Automated test suite covering catalog, basket, checkout and contact flows

## Project layout

- `bakery_site/` project settings, root URL configuration and WSGI entry points
- `catalog/` categories, products, catalog views and the seed command
- `orders/` basket, checkout services, order models, order views and admin
- `pages/` about page and contact form
- `templates/` shared layout and page templates
- `static/` stylesheet and small client script

## Requirements

- Python 3.11 or newer
- GNU Make (optional, for the shortcuts in the Makefile)

## Running locally

With Make:

    make install
    make migrate
    make seed
    make superuser
    make run

Then open http://127.0.0.1:8000/ in a browser. The Django admin is available at http://127.0.0.1:8000/admin/.

Without Make:

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_catalog
    python manage.py createsuperuser
    python manage.py runserver

## Configuration

Settings read the following environment variables:

- `DJANGO_SECRET_KEY` secret key, required outside development
- `DJANGO_DEBUG` set to `0` in production
- `DJANGO_ALLOWED_HOSTS` comma separated host names
- `DJANGO_CSRF_TRUSTED_ORIGINS` comma separated origins such as `https://shop.example.com`
- `DJANGO_SQLITE_PATH` path of the SQLite database file

The file `.env.example` lists the same variables.

## Testing

    make test

## Packaging

    make zip

The archive is written to `dist/hearth-and-crumb-django.zip` and contains the committed state of the repository.

## Production

Collect static files with `make static` and serve the application with gunicorn, for example `gunicorn -c deploy/gunicorn.conf.py bakery_site.wsgi:application`. A Dockerfile is included for container builds.
