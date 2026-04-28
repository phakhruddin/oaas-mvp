# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

Use this file as the companion operational record for every major implementation step in the repo.

## Current Status

```text
FastAPI API
  -> API key authentication
  -> SQS queue
  -> SQS worker
  -> DLQ handling
  -> CloudWatch metrics
  -> structured JSON logs
  -> trace correlation
  -> optional OpenTelemetry tracing
  -> AWS deployment skeleton
  -> multi-tenant worker
  -> CloudWatch logs
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: production hardening (IAM least privilege + autoscaling)
```

---

## Step 31 — API Authentication (Tenant Isolation)

Commit:

```text
feat(auth): add tenant api key field
feat(auth): add api key authentication dependency
feat(auth): enforce tenant api key authentication
```

Files changed:

```text
app/models/tenant.py
app/core/auth.py
app/api/main.py
```

Purpose:

Secure the API and enforce tenant-level isolation using API keys.

### Authentication Model

Each tenant is assigned an API key:

```text
TenantConfig.api_key
```

Requests must include:

```http
x-api-key: <tenant_api_key>
```

### Enforcement

- All endpoints use authentication dependency
- API resolves tenant from API key
- Tenant ID in path must match authenticated tenant

### Security Behavior

Missing API key:

```text
401 Unauthorized
```

Invalid API key:

```text
403 Forbidden
```

Cross-tenant access attempt:

```text
403 Tenant access denied
```

### Flow

```text
Client
  -> sends API key
FastAPI
  -> validates key
  -> resolves tenant
  -> enforces tenant isolation
Queue
  -> processes only authorized tenant jobs
```

### Result

- Prevents unauthorized access
- Ensures strict tenant isolation
- Enables SaaS multi-customer deployment

---

## Step 32 — OpenTelemetry Integration

Commit:

```text
feat(otel): add optional OpenTelemetry tracer
feat(otel): instrument API with spans
```

Files changed:

```text
app/core/otel.py
app/api/main.py
```

Purpose:

Introduce industry-standard distributed tracing using OpenTelemetry.

### Design

- Optional enablement through `ENABLE_OTEL=true`
- No-op fallback for local development
- OTLP exporter support through `OTEL_EXPORTER_OTLP_ENDPOINT`

### Flow

```text
API request
  -> start span: list_tenants / enqueue_job
  -> attach attributes: tenant_id, trace_id
  -> export span when OTEL is enabled
```

### Configuration

```bash
export ENABLE_OTEL=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Result

- Standard tracing foundation
- Compatible with Jaeger, Grafana Tempo, Datadog, Honeycomb, and OpenTelemetry Collector
- Keeps local mode safe when OTEL packages or collectors are unavailable

---

## Step 33 — AWS Deployment (ECS + SQS + API Gateway)

Commit:

```text
infra(terraform): add AWS deployment root module
infra(terraform): add variables for AWS deployment
infra(queue): add SQS + DLQ module
docs: add AWS deployment guide
```

Files changed:

```text
infra/terraform/main.tf
infra/terraform/variables.tf
infra/terraform/modules/queue/main.tf
docs/deployment-aws.md
```

Purpose:

Add the first AWS deployment skeleton for running OAAS as a cloud-native SaaS backend.

### Architecture

```text
Client
  -> API Gateway
  -> ECS Fargate API service
  -> SQS queue
  -> ECS Fargate worker service
  -> CloudWatch + Slack
```

### Components

- ECS Fargate for API and worker containers
- SQS main queue
- SQS dead-letter queue
- API Gateway as public entry point
- CloudWatch logs and metrics
- Terraform modules for repeatable deployment

### Deployment Flow

```text
1. Build Docker images
2. Push images to ECR
3. Run terraform init / plan / apply
4. Configure environment variables and secrets
5. Validate API Gateway, SQS queue depth, ECS logs, and Slack delivery
```

### Result

- Moves repo from local/distributed design to cloud deployment architecture
- Establishes AWS-native runtime target
- Prepares for IAM least privilege, autoscaling, and CI/CD

### Next Step

```text
next: production hardening (IAM least privilege + autoscaling)
```

---

## Known Follow-Ups

1. Restore or merge earlier runbook steps 1–30 if overwritten by later updates.
2. Wire rate limiter and circuit breaker into `workers/sqs_worker.py`.
3. Add DLQ replay tooling.
4. Add tests for queue failure paths.
5. Add CloudWatch dashboard definitions for queue metrics.
6. Add `send_text()` to `integrations/slack/slack_client.py` if not already present.
7. Verify `app/core/config.py` exists and is populated.
8. Add `config/tenants.example.json` so tenant setup is documented safely without secrets.
9. Update `.github/workflows/daily-digest.yml` to pass `SLACK_WEBHOOK_URL` if not already present.
10. Add `requirements.txt` with required packages.
11. Add IAM least-privilege policies and ECS autoscaling.
12. Add CI/CD from GitHub Actions to ECR/ECS.

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code or documentation change.
2. Add or update the matching runbook section.
3. Use semantic commit messages.
