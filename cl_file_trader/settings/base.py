# config/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_elasticsearch_dsl",
    "storages",
    "django_celery_beat",
    # apps
    "apps.accounts",
    "apps.files",
    "apps.subscriptions",
    # "apps.search",
    "apps.ads",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cl_file_trader.urls"
WSGI_APPLICATION = "cl_file_trader.wsgi.application"
AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL          = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ── i18n ──────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# ── Static / Media ────────────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── DRF ───────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}

# ── SimpleJWT ─────────────────────────────────────────────────────────────────
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_TIMEZONE                  = "UTC"
CELERY_TASK_TRACK_STARTED        = True
CELERY_TASK_TIME_LIMIT           = 30 * 60          # 30 min hard limit
CELERY_TASK_SOFT_TIME_LIMIT      = 25 * 60          # 25 min soft limit
CELERY_RESULT_BACKEND            = "redis://redis:6379/1"
CELERY_ACCEPT_CONTENT            = ["json"]
CELERY_TASK_SERIALIZER           = "json"
CELERY_BROKER_URL = "redis://redis:6379/0"

# ── Elasticsearch ─────────────────────────────────────────────────────────────
ELASTICSEARCH_DSL = {
    "default": {"hosts": os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")},
}

# ── Email (override per environment) ──────────────────────────────────────────
DEFAULT_FROM_EMAIL = "noreply@fileshare.pro"
SERVER_EMAIL       = "errors@fileshare.pro"

# ── File upload limits ────────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE  = 5 * 1024 * 1024 * 1024   # 5 GB absolute max
FILE_UPLOAD_MAX_MEMORY_SIZE  = 5 * 1024 * 1024 * 1024


# ══════════════════════════════════════════════════════════════════════════════
#  LOGGING
#  Hierarchy:  fileshare (root app logger)
#                ├── fileshare.accounts
#                ├── fileshare.files
#                ├── fileshare.subscriptions
#                ├── fileshare.search
#                ├── fileshare.ads
#                └── fileshare.celery
#
#  Usage anywhere in the project:
#      import logging
#      logger = logging.getLogger("fileshare.files")   # pick your app
#      logger.debug("detail only devs care about")
#      logger.info("file uploaded: %s", file_id)
#      logger.warning("quota almost full for user %s", user_id)
#      logger.error("S3 upload failed", exc_info=True)
#      logger.critical("payment webhook verification failed!")
# ══════════════════════════════════════════════════════════════════════════════
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,   # keep Django/library loggers alive

    # ── Formatters ────────────────────────────────────────────────────────────
    "formatters": {
        # Human-readable for development terminals
        "verbose": {
            "format": (
                "[{asctime}] {levelname:<8} {name:<30} "   # timestamp + level + logger name
                "pid={process} | {message}"                # process id + message
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style":   "{",
        },
        # Same but with file+line for debugging
        "verbose_with_location": {
            "format": (
                "[{asctime}] {levelname:<8} {name:<30} "
                "{filename}:{lineno} | {message}"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style":   "{",
        },
        # One-line compact for production log aggregators (Datadog, CloudWatch)
        # "json_line": {
        #     "()":      "apps.core.logging.JSONFormatter",   # custom (see below)
        #     "style":   "{",
        # },

        "json_line": {
            "format":  "{asctime} {levelname} {name} {message}",
            "style":   "{",
        },

        # Minimal for console during tests
        "simple": {
            "format":  "{levelname} {name} — {message}",
            "style":   "{",
        },
    },

    # ── Filters ───────────────────────────────────────────────────────────────
    "filters": {
        # Only emit if DEBUG=True
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        # Only emit if DEBUG=False  (used on error email handler)
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },

    # ── Handlers ──────────────────────────────────────────────────────────────
    "handlers": {

        # Pretty console — active in every environment
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
            "stream":    "ext://sys.stdout",
        },

        # Rotating file — one file per app, rolls at 10 MB, keeps 5 backups
        "file_app": {
            "class":        "logging.handlers.RotatingFileHandler",
            "filename":     BASE_DIR / "logs" / "app.log",
            "maxBytes":     10 * 1024 * 1024,   # 10 MB
            "backupCount":  5,
            "formatter":    "verbose_with_location",
            "encoding":     "utf-8",
        },

        # Separate file just for errors — easy to tail in production
        "file_errors": {
            "class":        "logging.handlers.RotatingFileHandler",
            "filename":     BASE_DIR / "logs" / "errors.log",
            "maxBytes":     10 * 1024 * 1024,
            "backupCount":  10,
            "formatter":    "verbose_with_location",
            "encoding":     "utf-8",
            "level":        "ERROR",
        },

        # Celery tasks get their own file — separates async noise from web
        "file_celery": {
            "class":        "logging.handlers.RotatingFileHandler",
            "filename":     BASE_DIR / "logs" / "celery.log",
            "maxBytes":     10 * 1024 * 1024,
            "backupCount":  5,
            "formatter":    "verbose_with_location",
            "encoding":     "utf-8",
        },

        # Email admins on ERROR+ (only in production — filtered below)
        "mail_admins": {
            "class":     "django.utils.log.AdminEmailHandler",
            "level":     "ERROR",
            "formatter": "verbose_with_location",
            "filters":   ["require_debug_false"],
        },

        # Null handler — silences noisy third-party loggers
        "null": {
            "class": "logging.NullHandler",
        },
    },

    # ── Loggers ───────────────────────────────────────────────────────────────
    "loggers": {

        # ── Your app loggers ──────────────────────────────────────────────────

        # Root for ALL fileshare code — catching anything that falls through
        "fileshare": {
            "handlers":  ["console", "file_app", "file_errors", "mail_admins"],
            "level":     "DEBUG",
            "propagate": False,
        },

        # Per-app loggers — inherit from "fileshare" if not defined,
        # but defined explicitly so you can change level per app independently
        "fileshare.accounts": {
            "handlers":  ["console", "file_app", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },
        "fileshare.files": {
            "handlers":  ["console", "file_app", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },
        "fileshare.subscriptions": {
            "handlers":  ["console", "file_app", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },
        "fileshare.search": {
            "handlers":  ["console", "file_app", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },
        "fileshare.ads": {
            "handlers":  ["console", "file_app", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },
        "fileshare.celery": {
            "handlers":  ["console", "file_celery", "file_errors"],
            "level":     "DEBUG",
            "propagate": False,
        },

        # ── Django internals ──────────────────────────────────────────────────
        "django": {
            "handlers":  ["console", "file_errors"],
            "level":     "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers":  ["file_errors", "mail_admins"],
            "level":     "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers":  ["file_errors", "mail_admins"],
            "level":     "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            # Set to DEBUG to see every SQL query — very noisy, dev only
            "handlers":  ["console"],
            "level":     "WARNING",
            "propagate": False,
        },

        # ── Third-party noise control ─────────────────────────────────────────
        "elasticsearch":       {"handlers": ["null"], "propagate": False},
        "urllib3":             {"handlers": ["null"], "propagate": False},
        "botocore":            {"handlers": ["null"], "propagate": False},
        "boto3":               {"handlers": ["null"], "propagate": False},
        "celery":              {"handlers": ["console", "file_celery"], "level": "INFO", "propagate": False},
        "celery.task":         {"handlers": ["file_celery"], "level": "INFO", "propagate": False},
        "stripe":              {"handlers": ["file_app"], "level": "WARNING", "propagate": False},
    },
}
