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
  -> IAM least privilege
  -> ECS autoscaling
  -> CI/CD pipeline
  -> Secrets Manager foundation
  -> blue/green deployment
  -> multi-region failover
  -> DynamoDB Global Tables
  -> region-aware routing
  -> conflict handling
  -> marketing capability mapping
  -> onboarding flow + API key issuance
  -> multi-tenant worker
  -> CloudWatch logs
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: write fencing + idempotency guarantees
```

---

(unchanged steps 1–41)

---

## Step 42 — Onboarding + API Key Issuance + Demo Tenant Flow

Commit:

feat(onboarding): add API key issuance helper  
feat(onboarding): add onboarding service for demo tenant  
feat(onboarding): add demo onboarding endpoint  
docs(onboarding): add onboarding flow

Files:

- app/core/api_keys.py
- app/services/onboarding.py
- app/api/main.py
- docs/onboarding.md

Purpose:

Enable users to quickly start using OAAS with minimal setup and achieve fast time-to-value.

### Flow

```text
User
  -> POST /onboarding/demo
  -> System creates demo tenant
  -> API key issued
  -> User receives next steps
```

### API Example

```text
POST /onboarding/demo
```

Response:

```json
{
  "tenant_id": "demo-tenant",
  "api_key": "oaas_xxx",
  "next_steps": ["connect logs", "run analyze"]
}
```

### Design

- Secure API key generation (hashed)
- Instant demo tenant provisioning
- No AWS setup required for initial experience

### Why this matters

Before:

```text
System exists but hard to start
```

After:

```text
User can try product in under 5 minutes
```

### Result

- Faster onboarding
- Better product adoption
- Clear demo flow

### Next Step

```text
next: write fencing + idempotency guarantees
```

---

## Known Follow-Ups

1. Wire rate limiter and circuit breaker into `workers/sqs_worker.py`.
2. Add DLQ replay tooling.
3. Add tests for queue failure paths.
4. Add CloudWatch dashboard definitions for queue metrics.
5. Add `send_text()` to `integrations/slack/slack_client.py` if not already present.
6. Verify `app/core/config.py` exists and is populated.
7. Add `config/tenants.example.json` so tenant setup is documented safely without secrets.
8. Update `.github/workflows/daily-digest.yml` to pass `SLACK_WEBHOOK_URL` if not already present.
9. Add `requirements.txt` with required packages.
10. Add CI/CD deployment validation and rollback checks.
11. Add blue/green deployment with ECS CodeDeploy.
12. Add DynamoDB Global Tables for replicated tenant/job state.
13. Add region-aware routing and write conflict handling.
14. Add write fencing tokens and idempotency enforcement.

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code or documentation change.
2. Add or update the matching runbook section.
3. Use semantic commit messages.
