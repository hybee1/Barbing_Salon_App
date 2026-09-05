# Barbing Salon App

A Django-based barbing salon management and appointment booking system.

The application provides a web interface and REST API for managing salon staff, services, bookings, break periods, inventory, salon settings and staff dashboards.

## Features

- Staff authentication
- JWT authentication using HTTP-only cookies
- Staff and salon-manager authorization
- Customer management
- Barber/stylist management
- Appointment/booking management
- Staff working schedules
- Break periods and off-days
- Salon services
- Hairstyles and colours
- Inventory management
- Dashboard statistics
- Reports
- User profile/image management
- Django administration
- REST API
- PostgreSQL support for production
- SQLite support for local development
- WhiteNoise support for serving production static files

## Technology Stack

- Python 3.12+
- Django 6
- Django REST Framework
- Simple JWT
- PostgreSQL
- SQLite for development
- Pillow
- django-cors-headers
- python-dotenv
- WhiteNoise for production static files

## Project Structure

```text
Barbing_Salon_App/
│
├── backend/
│   ├── accounts/
│   ├── bookings/
│   ├── breakperiods/
│   ├── custom_permissions/
│   ├── dashboard_auth_and_page/
│   ├── dashboard_stats/
│   ├── inventory/
│   ├── pagination/
│   ├── reports/
│   ├── salon_settings/
│   ├── services/
│   ├── session_and_jwt_auth/
│   └── utils/
│
├── core_config/
│   ├── settings_base.py
│   ├── settings_dev.py
│   ├── settings_prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── frontend/
│   ├── static/
│   ├── templates/
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env-dev
├── .env-prod
└── README.md
