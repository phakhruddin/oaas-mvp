import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.models.log_event import LogEvent


class CloudWatchLogReader:
    """Read log events from AWS CloudWatch Logs and convert them into LogEvent objects."""

    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError(
                    "boto3 is required for CloudWatch integration. Install with: pip install boto3"
                ) from exc

            self._client = boto3.client("logs", region_name=self.region_name)

        return self._client

    def read_recent_events(
        self,
        log_group_name: str,
        minutes: int = 15,
        filter_pattern: str = "",
        limit: int = 100,
        service_name: Optional[str] = None,
    ) -> List[LogEvent]:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)

        response = self.client.filter_log_events(
            logGroupName=log_group_name,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
            filterPattern=filter_pattern,
            limit=limit,
        )

        events: List[LogEvent] = []

        for item in response.get("events", []):
            message = item.get("message", "").strip()
            timestamp_ms = item.get("timestamp")
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

            events.append(
                LogEvent(
                    timestamp=timestamp,
                    service=service_name or self._infer_service(log_group_name),
                    level=self._infer_level(message),
                    message=message,
                    source="cloudwatch",
                    metadata={
                        "log_group": log_group_name,
                        "log_stream": item.get("logStreamName"),
                        "event_id": item.get("eventId"),
                    },
                )
            )

        return events

    def _infer_service(self, log_group_name: str) -> str:
        return log_group_name.strip("/").split("/")[-1] or "unknown-service"

    def _infer_level(self, message: str) -> str:
        lower_message = message.lower()

        if any(keyword in lower_message for keyword in ["critical", "fatal", "panic"]):
            return "critical"
        if any(keyword in lower_message for keyword in ["error", "exception", "failed", "timeout"]):
            return "error"
        if any(keyword in lower_message for keyword in ["warn", "warning", "retry"]):
            return "warning"

        return "info"
