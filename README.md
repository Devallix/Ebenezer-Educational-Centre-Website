# Ebenezer Educational Centre - School Website & Admin Dashboard

A complete, production-ready website for **Ebenezer Educational Centre**, a
preschool and primary school in Jukwa, Cape Coast, Ghana. It pairs a public
marketing site with a custom staff dashboard for managing every piece of
content, enquiries and analytics - no Django Admin knowledge required.

Built with **Django 5.2**, **Bootstrap 5**, **Crispy Forms** and **Chart.js**.

---

## Features

**Public website**
- Home page with an admin-managed photographic hero slideshow and benefits
- About page (vision, mission, proprietress' message)
- Classes and Programmes (curriculum) listing and detail pages
- Gallery with albums and a keyboard-accessible lightbox
- Contact page with location, phone, email and map (the message form is
  switched off in `templates/admissions/contact.html` for now)
- 404/500 pages, `robots.txt` and dynamic `sitemap.xml`
- Responsive, accessible, SEO-aware templates with Open Graph / Twitter cards
- Colour theme driven entirely by the dashboard (no code edits needed)

**Staff dashboard** (`/dashboard/`)
- Role-based access control (Super Admin, Website Admin, Enquiries Officer, Content Editor)
- Overview metrics and a full analytics module (views, visitors, devices, referrers, conversions)
- Full CRUD for slides, classes, teachers, programmes, gallery and benefits
- School profile, footer/social links and brand asset management
- Website appearance: 11 configurable brand colours with live preview and reset
- SEO settings (global + per-page overrides)
- Contact message inbox with archive/restore
- Email notification settings + delivery log
- User & role management, system maintenance and an audit log

**Engineering**
- A single, environment-driven settings module (`config/settings.py`)
- SQLite for development, PostgreSQL for production (via `DATABASE_URL`)
- WhiteNoise for static file serving; ready for Gunicorn + Nginx
- Custom role/capability layer with a real test suite

---

## Requirements

- Python 3.11+ (developed and tested on Python 3.14)
- pip and virtualenv
- SQLite (bundled) for development, or PostgreSQL for production

---

## Quick start (development)

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
# source .venv/bin/activate          # macOS / Linux

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Configure the environment
Copy-Item .env.example .env          # then edit .env if needed

# 4. Create the database
python manage.py migrate

# 5. Seed starter data (classes, learning areas, benefits) and roles
python manage.py seed_school_data
python manage.py setup_roles

# 6. Create the first administrator
python manage.py create_initial_admin

# 7. Run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the website and
<http://127.0.0.1:8000/dashboard/> for the dashboard.

> On Windows PowerShell the command is `python manage.py ...` (the bare
> `django` / `django-admin` shim is not required and may not be on `PATH`).

---

## Management commands

| Command | Purpose |
| --- | --- |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create a Django superuser |
| `python manage.py create_initial_admin` | Create the bootstrap admin from `ADMIN_*` env vars |
| `python manage.py setup_roles` | Create the four dashboard role groups |
| `python manage.py seed_school_data` | Seed classes, learning areas and benefits (idempotent) |
| `python manage.py collectstatic` | Collect static files for production |
| `python manage.py test` | Run the test suite |

---

## Roles & permissions

Roles map to Django groups created by `setup_roles`. The dashboard menu and
every view enforce these capabilities (superusers always have full access).

| Role | Group | Highlights |
| --- | --- | --- |
| Super Administrator | Super Administrators | Everything, including users and system settings |
| Website Administrator | Website Administrators | Content, appearance, SEO, settings, notifications |
| Enquiries Officer | Enquiries Officers | Contact messages |
| Content Editor | Content Editors | Slideshow, classes, teachers, programmes, gallery |

---

## Project layout

```
config/            Single settings module, root URLconf, WSGI/ASGI
apps/
  core/            Site settings, theme, notifications, audit log, shared base models
  accounts/        Login, password reset, roles & capability helpers
  school/          Homepage slideshow + school benefits
  academics/       Classes, teachers, learning areas, class programmes
  admissions/      Contact messages (public contact form)
  gallery/         Albums and images
  dashboard/       All /dashboard/ views and URLs
  analytics/       Privacy-friendly pageview tracking + reporting
  seo/             Global/page SEO, sitemap, robots
static/            Source CSS/JS/images (main + dashboard)
templates/         Public, dashboard and account templates
tests/             Test suite
scripts/           Maintenance / bootstrap helpers
deployment/        Gunicorn, Nginx and systemd samples
```

---

## Testing

```powershell
python manage.py test
```

The suite covers public pages, the authentication flow, 404 handling, the
sitemap/robots endpoints, and every dashboard page renders successfully for an
authorised user.

---

## Deployment

See [`deployment/README.md`](deployment/README.md) for a step-by-step
production guide (PostgreSQL, Gunicorn, Nginx, systemd, static files, HTTPS and
backups).

---

## Content notes

- Starter data (classes, learning areas, benefits) is intentionally minimal and
  **must be reviewed** to match the school's real offerings.
- Placeholder SVGs (`static/images/placeholder.svg`) stand in for missing
  imagery. Upload real photos and a logo through the dashboard.
- No fabricated statistics, staff or testimonials are included anywhere.
