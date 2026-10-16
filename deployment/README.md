# Deployment guide

This guide targets a standard Linux server (Ubuntu/Debian) running
**PostgreSQL**, **Gunicorn** behind **Nginx**, managed by **systemd**.

The same single settings module (`config/settings.py`) powers development and
production; the difference is entirely driven by environment variables.

---

## 1. Server packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib
```

Create a dedicated system user and deploy the code:

```bash
sudo adduser --system --group --home /opt/ebenezer ebeneezer
sudo -u ebeneezer git clone <your-repo-url> /opt/ebenezer/app
cd /opt/ebenezer/app
```

## 2. Python environment

```bash
sudo -u ebeneezer python3 -m venv /opt/ebenezer/venv
sudo -u ebeneezer /opt/ebenezer/venv/bin/pip install -r requirements.txt
```

## 3. PostgreSQL database

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE ebenezer;
CREATE USER ebenezer WITH ENCRYPTED PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE ebenezer TO ebenezer;
ALTER DATABASE ebenezer OWNER TO ebenezer;
SQL
```

## 4. Environment file

Copy `.env.example` to `/opt/ebenezer/app/.env` and set production values:

```ini
DEBUG=False
SECRET_KEY=<long-random-value>
ALLOWED_HOSTS=ebenezer.edu.gh,www.ebenezer.edu.gh
CSRF_TRUSTED_ORIGINS=https://ebenezer.edu.gh,https://www.ebenezer.edu.gh
SITE_URL=https://ebenezer.edu.gh

DATABASE_URL=postgres://ebenezer:change-me@127.0.0.1:5432/ebenezer
DATABASE_SSL_REQUIRE=False

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=notifications@ebenezer.edu.gh
EMAIL_HOST_PASSWORD=<smtp-password>
DEFAULT_FROM_EMAIL=Ebenezer Educational Centre <notifications@ebenezer.edu.gh>
SCHOOL_NOTIFICATION_EMAIL=admin@ebenezer.edu.gh

REQUIRE_PRODUCTION_DB=True
SECURE_SSL_REDIRECT=True
LOG_LEVEL=INFO
```

> When `DEBUG=False` the project **refuses to start** with the default insecure
> key, an empty `ALLOWED_HOSTS`, or (with `REQUIRE_PRODUCTION_DB=True`) no
> `DATABASE_URL`. This prevents accidentally shipping an unsafe configuration.

## 5. Migrate, seed and collect static files

```bash
cd /opt/ebenezer/app
sudo -u ebeneezer /opt/ebenezer/venv/bin/python manage.py migrate
sudo -u ebeneezer /opt/ebenezer/venv/bin/python manage.py setup_roles
sudo -u ebeneezer /opt/ebenezer/venv/bin/python manage.py seed_school_data
sudo -u ebeneezer /opt/ebenezer/venv/bin/python manage.py collectstatic --noinput
sudo -u ebeneezer /opt/ebenezer/venv/bin/python manage.py create_initial_admin
```

## 6. Gunicorn + systemd

Install the unit file and adjust paths/user if needed:

```bash
sudo cp deployment/gunicorn.service /etc/systemd/system/ebenezer.service
sudo systemctl daemon-reload
sudo systemctl enable --now ebenezer
sudo systemctl status ebenezer
```

## 7. Nginx

```bash
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ebenezer
sudo ln -s /etc/nginx/sites-available/ebenezer /etc/nginx/sites-enabled/ebenezer
sudo nginx -t && sudo systemctl reload nginx
```

## 8. HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ebenezer.edu.gh -d www.ebenezer.edu.gh
```

WhiteNoise serves collected static files directly; Nginx serves `media/` and
proxies everything else to Gunicorn.

## 9. Backups

Back up the database and uploaded media on a schedule:

```bash
# Database
pg_dump -U ebenezer ebenezer | gzip > /backups/ebenezer-$(date +%F).sql.gz

# Media (uploaded logos, photos, gallery images)
tar czf /backups/ebenezer-media-$(date +%F).tar.gz /opt/ebenezer/app/media
```

Add both to `cron` and copy the archives off-server.

## 10. Routine maintenance

- **Analytics retention** - old pageview events are purged from
  *Dashboard -> System -> Purge old analytics events* (window controlled by
  `ANALYTICS_RETENTION_DAYS`).
- **Updates** - `git pull`, `pip install -r requirements.txt`,
  `manage.py migrate`, `manage.py collectstatic`, then
  `sudo systemctl restart ebenezer`.
- **Logs** - `journalctl -u ebenezer -f` for application logs; Nginx logs under
  `/var/log/nginx/`.

---

## Scaling checklist

- [ ] `DEBUG=False` and a strong `SECRET_KEY`
- [ ] PostgreSQL via `DATABASE_URL` with `REQUIRE_PRODUCTION_DB=True`
- [ ] `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set to real domains
- [ ] HTTPS enabled (`SECURE_SSL_REDIRECT=True`, HSTS on)
- [ ] SMTP email configured and tested via the notification log
- [ ] `collectstatic` run and static files served
- [ ] Scheduled database + media backups
- [ ] A superuser created and other staff assigned roles
