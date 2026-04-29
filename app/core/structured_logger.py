import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

trace_id_context: ContextVar[str] = ContextVar("trace_id", default="")
tenant_id_context: ContextVar[str] = ContextVar("tenant_id", default="")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None) or trace_id_context.get() or None,
            "tenant_id": getattr(record, "tenant_id", None) or tenant_id_context.get() or None,
        }

        for key in ["job_type", "source_name", "queue_name", "duration_ms"]:
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(context)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def set_log_context(trace_id: Optional[str] = None, tenant_id: Optional[str] = None) -> None:
    if trace_id:
        trace_id_context.set(trace_id)
    if tenant_id:
        tenant_id_context.set(tenant_id)


def clear_log_context() -> None:
    trace_id_context.set("")
    tenant_id_context.set("")


def log_event(
    logger: logging.Logger,
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra={"context": context or {}})
