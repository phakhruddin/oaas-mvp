from fastapi import HTTPException, Header
from typing import Optional

from app.core.tenant_loader import TenantLoader


def authenticate(api_key: Optional[str] = Header(None, alias="x-api-key")):
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    tenants = TenantLoader().load()

    for tenant in tenants:
        if tenant.api_key and tenant.api_key == api_key:
            return tenant

    raise HTTPException(status_code=403, detail="Invalid API key")
