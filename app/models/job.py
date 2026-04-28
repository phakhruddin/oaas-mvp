from dataclasses import dataclass
from typing import Dict, Optional
import uuid


@dataclass
class AnalysisJob:
    job_type: str
    tenant_id: str
    source_name: Optional[str] = None
    metadata: Dict[str, str] | None = None
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, object]:
        return {
            "job_type": self.job_type,
            "tenant_id": self.tenant_id,
            "source_name": self.source_name,
            "metadata": self.metadata or {},
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "AnalysisJob":
        return cls(
            job_type=str(payload["job_type"]),
            tenant_id=str(payload["tenant_id"]),
            source_name=payload.get("source_name") if payload.get("source_name") else None,
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
            correlation_id=payload.get("correlation_id"),
        )
