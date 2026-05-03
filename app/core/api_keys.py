import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class IssuedApiKey:
    tenant_id: str
    api_key: str
    api_key_hash: str
    issued_at: str


def generate_api_key(prefix: str = "oaas") -> str:
    token = secrets.token_urlsafe(32)
    return f"{prefix}_{token}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def issue_api_key(tenant_id: str) -> IssuedApiKey:
    api_key = generate_api_key()
    return IssuedApiKey(
        tenant_id=tenant_id,
        api_key=api_key,
        api_key_hash=hash_api_key(api_key),
        issued_at=datetime.now(timezone.utc).isoformat(),
    )
