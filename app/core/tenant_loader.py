import json
from pathlib import Path
from typing import List

from app.models.tenant import TenantConfig, TenantLogSource


class TenantLoader:
    """Load tenant configuration from a JSON file."""

    def __init__(self, config_path: str = "config/tenants.json"):
        self.config_path = Path(config_path)

    def load(self) -> List[TenantConfig]:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Tenant config not found: {self.config_path}. "
                "Create config/tenants.json or pass TENANT_CONFIG_PATH."
            )

        payload = json.loads(self.config_path.read_text())
        tenants = []

        for item in payload.get("tenants", []):
            log_sources = [
                TenantLogSource(
                    name=source["name"],
                    provider=source.get("provider", "cloudwatch"),
                    log_group=source["log_group"],
                    region=source.get("region", "us-east-1"),
                    service_name=source.get("service_name"),
                    filter_pattern=source.get("filter_pattern", ""),
                    lookback_minutes=int(source.get("lookback_minutes", 15)),
                    limit=int(source.get("limit", 100)),
                )
                for source in item.get("log_sources", [])
            ]

            tenants.append(
                TenantConfig(
                    tenant_id=item["tenant_id"],
                    display_name=item.get("display_name", item["tenant_id"]),
                    slack_webhook_url=item.get("slack_webhook_url"),
                    use_llm=bool(item.get("use_llm", False)),
                    metadata=item.get("metadata", {}),
                    log_sources=log_sources,
                )
            )

        return tenants
