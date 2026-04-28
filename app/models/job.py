from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AnalysisJob:
    job_type: str
    tenant_id: str
    source_name: Optional[str] = None
    metadata: Dict[str, str] | None = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "job_type": self.job_type,
            "tenant_id": self.tenant_id,
            "source_name": self.source_name,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "AnalysisJob":
        return cls(
            job_type=str(payload["job_type"]),
            tenant_id=str(payload["tenant_id"]),
            source_name=payload.get("source_name") if payload.get("source_name") else None,
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        )
