import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ["trace_id", "tenant_id", "job_type", "source_name"]:
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        return json.dumps(payload)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
