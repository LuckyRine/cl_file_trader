# config/settings/production.py
from .base import *

DEBUG         = True
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
SECRET_KEY    = os.environ["SECRET_KEY"]   # must be set — crash early if missing

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.environ["POSTGRES_DB"],
        "USER":     os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST":     os.environ["POSTGRES_HOST"],
        "PORT":     os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,       # persistent connections
        "OPTIONS":  {"sslmode": "require"},
    }
}

# ── Cache / Celery broker ─────────────────────────────────────────────────────
REDIS_URL = os.environ["REDIS_URL"]   # e.g. redis://:password@host:6379/0

CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS":  {"socket_connect_timeout": 5, "socket_timeout": 5},
    }
}
CELERY_BROKER_URL = REDIS_URL

# ── Storage — AWS S3 ─────────────────────────────────────────────────────────
DEFAULT_FILE_STORAGE  = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE   = "storages.backends.s3boto3.S3StaticStorage"

AWS_STORAGE_BUCKET_NAME      = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME           = os.environ.get("AWS_S3_REGION_NAME", "eu-west-1")
AWS_S3_FILE_OVERWRITE        = False
AWS_DEFAULT_ACL              = None        # use bucket policy, not object ACL
AWS_S3_OBJECT_PARAMETERS     = {"CacheControl": "max-age=86400"}
AWS_QUERYSTRING_AUTH         = True        # presigned URLs
AWS_QUERYSTRING_EXPIRE       = 300         # presigned URL valid for 5 minutes

# ── Email — SES / SMTP ───────────────────────────────────────────────────────
EMAIL_BACKEND  = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST     = os.environ.get("EMAIL_HOST",     "email-smtp.eu-west-1.amazonaws.com")
EMAIL_PORT     = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS  = True
EMAIL_HOST_USER     = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]

# ── Security headers ──────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = "DENY"

# ── Admins — receive error emails ─────────────────────────────────────────────
ADMINS = [("FileShare Admin", os.environ.get("ADMIN_EMAIL", "admin@fileshare.pro"))]

# ── Production logging overrides ─────────────────────────────────────────────
# In production we raise the floor to INFO (no debug noise) and
# switch the console formatter to the compact JSON line format so
# log aggregators (Datadog, CloudWatch, Loki) can parse structured fields.
LOGGING["handlers"]["console"]["formatter"] = "json_line"

for _name, _cfg in LOGGING["loggers"].items():
    if _cfg.get("level") == "DEBUG":
        _cfg["level"] = "INFO"
