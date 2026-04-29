import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class RegionDecision:
    tenant_id: str
    operation: str
    selected_region: str
    reason: str


class RegionRouter:
    """Region-aware routing helper.

    Reads use the local region by default for low latency.
    Writes use a configured primary writer region unless tenant metadata overrides it.
    """

    def __init__(self, local_region: Optional[str] = None, primary_write_region: Optional[str] = None):
        self.local_region = local_region or os.getenv("AWS_REGION", "us-east-1")
        self.primary_write_region = primary_write_region or os.getenv("PRIMARY_WRITE_REGION", self.local_region)

    def route(
        self,
        tenant_id: str,
        operation: str,
        tenant_metadata: Optional[Dict[str, str]] = None,
    ) -> RegionDecision:
        metadata = tenant_metadata or {}
        operation_lower = operation.lower()

        if operation_lower == "read":
            return RegionDecision(
                tenant_id=tenant_id,
                operation=operation_lower,
                selected_region=metadata.get("preferred_read_region", self.local_region),
                reason="reads prefer the local or tenant-preferred region",
            )

        if operation_lower == "write":
            return RegionDecision(
                tenant_id=tenant_id,
                operation=operation_lower,
                selected_region=metadata.get("preferred_write_region", self.primary_write_region),
                reason="writes are routed to the configured primary writer region to reduce conflicts",
            )

        return RegionDecision(
            tenant_id=tenant_id,
            operation=operation_lower,
            selected_region=self.local_region,
            reason="unknown operation defaults to local region",
        )


class ConflictResolver:
    """Simple last-writer-wins conflict helper for replicated records.

    This does not replace application-level idempotency. It provides a small,
    explicit policy for comparing replicated versions.
    """

    def choose_winner(self, current_record: Dict, incoming_record: Dict) -> Dict:
        current_updated_at = self._parse_timestamp(current_record.get("updated_at"))
        incoming_updated_at = self._parse_timestamp(incoming_record.get("updated_at"))

        if incoming_updated_at >= current_updated_at:
            return incoming_record

        return current_record

    def build_versioned_record(self, payload: Dict, region: str) -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        record = dict(payload)
        record["updated_at"] = now
        record["updated_by_region"] = region
        return record

    def _parse_timestamp(self, value: Optional[str]) -> datetime:
        if not value:
            return datetime.fromtimestamp(0, timezone.utc)

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.fromtimestamp(0, timezone.utc)
