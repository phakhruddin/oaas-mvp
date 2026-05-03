import hashlib
import time
from dataclasses import dataclass
from typing import Dict, Optional


class WriteFenceRejected(Exception):
    pass


class DuplicateOperation(Exception):
    pass


@dataclass
class FenceToken:
    tenant_id: str
    region: str
    token: int
    issued_at_epoch: float


class WriteFence:
    """In-memory write fencing helper.

    A real production implementation should persist fence tokens in DynamoDB
    using conditional writes. This class models the policy used by the service:
    every write must carry a monotonic token, and stale tokens are rejected.
    """

    def __init__(self):
        self._latest_tokens: Dict[str, int] = {}

    def issue_token(self, tenant_id: str, region: str) -> FenceToken:
        key = self._key(tenant_id, region)
        next_token = self._latest_tokens.get(key, 0) + 1
        self._latest_tokens[key] = next_token

        return FenceToken(
            tenant_id=tenant_id,
            region=region,
            token=next_token,
            issued_at_epoch=time.time(),
        )

    def validate(self, token: FenceToken) -> None:
        key = self._key(token.tenant_id, token.region)
        latest = self._latest_tokens.get(key, 0)

        if token.token < latest:
            raise WriteFenceRejected(
                f"stale fence token for tenant={token.tenant_id}, region={token.region}"
            )

        self._latest_tokens[key] = token.token

    def _key(self, tenant_id: str, region: str) -> str:
        return f"{tenant_id}:{region}"


class IdempotencyStore:
    """In-memory idempotency helper.

    A real production implementation should persist keys in DynamoDB with TTL.
    This class prevents duplicate operation execution during retries.
    """

    def __init__(self):
        self._seen: Dict[str, Dict] = {}

    def build_key(self, tenant_id: str, operation: str, payload: Dict) -> str:
        digest = hashlib.sha256(str(sorted(payload.items())).encode("utf-8")).hexdigest()
        return f"{tenant_id}:{operation}:{digest}"

    def check_or_record(self, idempotency_key: str, response: Optional[Dict] = None) -> Optional[Dict]:
        if idempotency_key in self._seen:
            return self._seen[idempotency_key]

        self._seen[idempotency_key] = response or {"status": "accepted"}
        return None


write_fence = WriteFence()
idempotency_store = IdempotencyStore()
