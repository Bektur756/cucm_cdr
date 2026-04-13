# CUCM CDR Portal

Internal Django web app for browsing CUCM CDR records stored in PostgreSQL.

## Features

- Django server-rendered UI with Bootstrap
- Built-in Django authentication for login/logout
- Auth-protected CDR list page
- Unmanaged Django model mapped to existing `cucm_cdr` table
- Phone number search across multiple CUCM fields
- Start/end date filters on `date_time_origination`
- Pagination with 100 rows per page
- Excel export for the currently filtered result set
- Query optimization by selecting only displayed columns
- Containerized deployment with Gunicorn behind Nginx

## Project Structure

```text
cdr_parser/
├── .env.example
├── Dockerfile
├── README.md
├── deploy/
│   └── nginx/
│       └── default.conf
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── cdr/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── cdr_portal/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── templates/
    ├── base.html
    ├── registration/
    │   ├── logged_out.html
    │   └── login.html
    └── cdr/
        └── cdr_list.html
```

## Local Setup

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file:

```bash
cp .env .env
```

3. Run Django migrations for built-in apps only:

```bash
python manage.py migrate
```

This will create Django auth/session/admin tables. It does not recreate or modify `cucm_cdr`.

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Start the app:

```bash
python manage.py runserver
```

6. Open:

```text
http://127.0.0.1:8000/
```

## Docker

```bash
cp .env .env
docker compose up --build
```

Nginx listens on port `80` and proxies requests to Gunicorn in the `web` container.

Run migrations and create a superuser in the container:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open:

```text
http://127.0.0.1/
```

## How It Works

- `cdr_portal/settings.py` reads PostgreSQL and Django configuration from environment variables.
- `cdr/models.py` maps the existing `cucm_cdr` table with `managed = False`.
- `cdr/forms.py` defines the GET-based search/filter form.
- `cdr/views.py` applies phone/date filters, limits selected columns, orders by origination date descending, paginates 100 rows per page, and exports the filtered result set to Excel.
- `templates/` contains Bootstrap-based login/logout and CDR list pages.
- `deploy/nginx/default.conf` proxies HTTP traffic to Gunicorn in the `web` container.

## Important Note About the Model Primary Key

The unmanaged model uses `global_call_id_call_id` as the Django primary key because Django ORM requires one. In many CUCM exports this column exists, but if your `cucm_cdr` table uses a different unique key, update the model field in `cdr/models.py` to match your actual table definition.

## Recommended PostgreSQL Indexes

For large CDR tables, add indexes directly in PostgreSQL, not via Django migrations:

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS cucm_cdr_date_time_origination_idx
ON cucm_cdr (date_time_origination DESC);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX CONCURRENTLY IF NOT EXISTS cucm_cdr_calling_party_number_trgm_idx
ON cucm_cdr USING gin (calling_party_number gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS cucm_cdr_original_called_party_number_trgm_idx
ON cucm_cdr USING gin (original_called_party_number gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS cucm_cdr_final_called_party_number_trgm_idx
ON cucm_cdr USING gin (final_called_party_number gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS cucm_cdr_last_redirect_dn_trgm_idx
ON cucm_cdr USING gin (last_redirect_dn gin_trgm_ops);
```

`pg_trgm` indexes are recommended because the UI uses partial matching with `icontains`.
# cucm_cdr
