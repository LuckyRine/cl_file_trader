# config/settings/development.py
from .base import *

DEBUG      = True
ALLOWED_HOSTS = ["*"]

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.environ.get("POSTGRES_DB",       "fileshare"),
        "USER":     os.environ.get("POSTGRES_USER",     "fileshare"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "secret"),
        "HOST":     os.environ.get("POSTGRES_HOST",     "db"),
        "PORT":     os.environ.get("POSTGRES_PORT",     "5432"),
    }
}

# ── Cache / Celery broker ─────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/0",
    }
}
CELERY_BROKER_URL = "redis://redis:6379/0"

# ── Storage — local disk in dev ───────────────────────────────────────────────
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# ── Email — print to console ──────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Dev-only: show all SQL queries ───────────────────────────────────────────
# Uncomment the block below to turn on SQL logging for a session.
# LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"

# ── Django Debug Toolbar (optional) ──────────────────────────────────────────
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]

# ── Dev overrides to logging defined in base.py ───────────────────────────────
# In development we want DEBUG on the console but don't need the mail_admins
# handler firing, so remove it from every logger that has it.
import copy, logging

for _name, _cfg in LOGGING["loggers"].items():
    if "mail_admins" in _cfg.get("handlers", []):
        _cfg["handlers"] = [h for h in _cfg["handlers"] if h != "mail_admins"]

# Also drop logging level of the root fileshare logger to DEBUG so you see
# every logger.debug() call in your terminal during development.
LOGGING["loggers"]["fileshare"]["level"] = "DEBUG"
