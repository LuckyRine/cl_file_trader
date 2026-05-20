# apps/core/logging.py
"""
Custom logging utilities for FileShare Pro.

Provides:
  - JSONFormatter  — structured one-line JSON logs for production aggregators
  - get_logger()   — thin convenience wrapper so every module uses the right
                     logger name without remembering the "fileshare." prefix
  - log_request()  — decorator that logs entry/exit of any view function
  - TaskLogger     — mixin for Celery tasks that adds task_id to every record
"""

import json
import logging
import time
import traceback
from functools import wraps


# ── JSON formatter ────────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """
    Emits one JSON object per line.  Fields:
        ts        — ISO-8601 timestamp
        level     — DEBUG / INFO / WARNING / ERROR / CRITICAL
        logger    — logger name  (e.g. fileshare.files)
        msg       — the formatted log message
        pid       — process id
        file      — source file:line
        exc       — exception traceback (only on exc_info records)
        extra.*   — any extra= kwargs passed to the logger call
    """

    RESERVED = {
        "args", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "message",
        "module", "msecs", "msg", "name", "pathname", "process",
        "processName", "relativeCreated", "stack_info", "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts":     self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.getMessage(),
            "pid":    record.process,
            "file":   f"{record.filename}:{record.lineno}",
        }

        # Attach exception traceback if present
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        # Any extra= keys passed by the caller end up as top-level fields
        for key, value in record.__dict__.items():
            if key not in self.RESERVED and not key.startswith("_"):
                try:
                    json.dumps(value)   # only include JSON-serialisable values
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = str(value)

        return json.dumps(payload, ensure_ascii=False)


# ── Logger factory ────────────────────────────────────────────────────────────

def get_logger(app: str) -> logging.Logger:
    """
    Return the correct fileshare.* logger for an app module.

    Usage:
        # at module level — no need to import logging directly
        from apps.core.logging import get_logger
        logger = get_logger("files")

        logger.info("upload started", extra={"user_id": str(user.id)})
        logger.error("S3 failed", exc_info=True, extra={"file_id": str(f.id)})

    Valid app names: accounts, files, subscriptions, search, ads, celery
    The resulting logger name will be  fileshare.<app>.
    """
    return logging.getLogger(f"fileshare.{app}")


# ── Request logging decorator ─────────────────────────────────────────────────

def log_request(logger: logging.Logger = None, level: int = logging.INFO):
    """
    Decorator for Django view functions (function-based or class method).
    Logs method + path on entry and status + elapsed time on exit.

    Usage:
        from apps.core.logging import log_request, get_logger
        logger = get_logger("files")

        @log_request(logger)
        def my_view(request, slug):
            ...

        # On DRF APIView use inside the method:
        @log_request(logger, level=logging.DEBUG)
        def post(self, request):
            ...
    """
    if logger is None:
        logger = get_logger("core")

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # args[0] is `self` for methods, `request` for functions
            request = args[1] if hasattr(args[0], "request") else args[0]

            start = time.perf_counter()
            logger.log(
                level,
                "→ %s %s",
                request.method,
                request.path,
                extra={
                    "user_id": str(request.user.pk) if request.user.is_authenticated else None,
                    "ip":      _get_client_ip(request),
                },
            )

            try:
                response = view_func(*args, **kwargs)
            except Exception:
                elapsed = (time.perf_counter() - start) * 1000
                logger.error(
                    "✗ %s %s raised after %.1fms",
                    request.method, request.path, elapsed,
                    exc_info=True,
                )
                raise

            elapsed = (time.perf_counter() - start) * 1000
            logger.log(
                level,
                "← %s %s %s %.1fms",
                request.method,
                request.path,
                getattr(response, "status_code", "?"),
                elapsed,
            )
            return response

        return wrapper
    return decorator


def _get_client_ip(request) -> str:
    """Extract real IP, respecting X-Forwarded-For from proxies/load balancers."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


# ── Celery task logger mixin ──────────────────────────────────────────────────

class TaskLogger:
    """
    Mixin for Celery tasks (bind=True) that injects task_id into every
    log record automatically so you can filter logs by task in aggregators.

    Usage:
        from celery import shared_task
        from apps.core.logging import TaskLogger, get_logger

        base_logger = get_logger("celery")

        @shared_task(bind=True, base=TaskLogger)
        def process_file(self, file_id: str):
            self.log.info("starting", extra={"file_id": file_id})
            ...
            self.log.info("done in %.2fs", elapsed)
    """

    @property
    def log(self) -> logging.LoggerAdapter:
        return _TaskLoggerAdapter(
            get_logger("celery"),
            {"task_id": self.request.id, "task_name": self.name},
        )


class _TaskLoggerAdapter(logging.LoggerAdapter):
    """Prepends task_id to every log record from a Celery task."""

    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        extra.update(self.extra)
        return msg, kwargs
