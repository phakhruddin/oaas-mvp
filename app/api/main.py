from fastapi import FastAPI, HTTPException

from app.core.tenant_loader import TenantLoader
from app.models.job import AnalysisJob
from integrations.aws.sqs_client import SQSClient

app = FastAPI(
    title="OAAS MVP API",
    description="AI-powered Observability-as-a-Service MVP API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "oaas-mvp"}


@app.get("/tenants")
def list_tenants():
    tenants = TenantLoader().load()

    return {
        "count": len(tenants),
        "tenants": [
            {
                "tenant_id": tenant.tenant_id,
                "display_name": tenant.display_name,
                "use_llm": tenant.use_llm,
                "log_source_count": len(tenant.log_sources),
            }
            for tenant in tenants
        ],
    }


@app.post("/tenants/{tenant_id}/analyze")
def analyze_tenant(tenant_id: str):
    tenants = TenantLoader().load()
    tenant = next((item for item in tenants if item.tenant_id == tenant_id), None)

    if tenant is None:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")

    job = AnalysisJob(job_type="analyze", tenant_id=tenant.tenant_id)
    sqs = SQSClient()
    sqs.send_message(job.to_dict())

    return {
        "tenant_id": tenant.tenant_id,
        "job_type": job.job_type,
        "status": "queued",
    }
