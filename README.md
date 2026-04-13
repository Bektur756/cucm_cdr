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
- Docker-only runtime workflow

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

## Docker Usage

```bash
cp .env.example .env
docker compose up --build
```

The image installs Python dependencies with `uv`, then runs Django behind Gunicorn. Nginx listens on port `80` and proxies requests to the `web` container.

Run migrations and create a superuser in the container:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open:

```text
http://127.0.0.1/
```

This creates Django auth/session/admin tables only. It does not recreate or modify `cucm_cdr`.

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
