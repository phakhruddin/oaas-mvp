from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime


@dataclass
class LogEvent:
    timestamp: datetime
    service: str
    level: str
    message: str
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_error(self) -> bool:
        return self.level.lower() in ["error", "critical"]

    def is_warning(self) -> bool:
        return self.level.lower() in ["warn", "warning"]

    def summary_key(self) -> str:
        """
        Generate a simplified key for grouping similar logs
        """
        return f"{self.service}:{self.level}:{self.message[:50]}"
