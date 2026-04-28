from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TenantLogSource:
    name: str
    provider: str
    log_group: str
    region: str
    service_name: Optional[str] = None
    filter_pattern: str = ""
    lookback_minutes: int = 15
    limit: int = 100


@dataclass
class TenantConfig:
    tenant_id: str
    display_name: str
    api_key: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    use_llm: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    log_sources: List[TenantLogSource] = field(default_factory=list)
