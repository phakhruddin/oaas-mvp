from fastapi import FastAPI, HTTPException, Depends

from app.core.logger import get_logger
from app.core.trace import generate_trace_id
from app.core.auth import authenticate
from app.core.otel import start_span, setup_otel
from app.models.job import AnalysisJob
from integrations.aws.sqs_client import SQSClient
from app.services.onboarding import OnboardingService

setup_otel("oaas-api")

app = FastAPI(
    title="OAAS MVP API",
    description="AI-powered Observability-as-a-Service MVP API",
    version="0.1.0",
)

logger = get_logger("api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "oaas-mvp"}


@app.post("/onboarding/demo")
def onboarding_demo():
    service = OnboardingService()
    return service.onboarding_response("demo-tenant")


@app.get("/tenants")
def list_tenants(current_tenant=Depends(authenticate)):
    with start_span("list_tenants", tenant_id=current_tenant.tenant_id):
        return {
            "tenant_id": current_tenant.tenant_id,
            "display_name": current_tenant.display_name,
            "use_llm": current_tenant.use_llm,
            "log_source_count": len(current_tenant.log_sources),
        }


@app.post("/tenants/{tenant_id}/analyze")
def analyze_tenant(tenant_id: str, current_tenant=Depends(authenticate)):
    if tenant_id != current_tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")

    trace_id = generate_trace_id()

    with start_span("enqueue_job", tenant_id=current_tenant.tenant_id, trace_id=trace_id):
        logger.info(
            "enqueue tenant job",
            extra={"trace_id": trace_id, "tenant_id": current_tenant.tenant_id},
        )

        job = AnalysisJob(
            job_type="analyze",
            tenant_id=current_tenant.tenant_id,
            metadata={"trace_id": trace_id},
        )

        sqs = SQSClient()
        sqs.send_message(job.to_dict())

        return {
            "tenant_id": current_tenant.tenant_id,
            "status": "queued",
            "trace_id": trace_id,
        }
