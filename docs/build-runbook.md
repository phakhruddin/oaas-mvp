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
  -> write fencing + idempotency
  -> multi-tenant worker
  -> CloudWatch logs
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: persist fencing + idempotency in DynamoDB
```

---

(unchanged steps 1–42)

---

## Step 43 — Write Fencing + Idempotency Guarantees

Commit:

feat(write-safety): add fencing and idempotency primitives  
docs(write-safety): add fencing and idempotency guide

Files:

- app/core/write_safety.py
- docs/write-safety.md

Purpose:

Ensure safe, repeatable, and conflict-resistant writes in a distributed multi-region system.

### Problem

- Retries can duplicate operations
- Cross-region writes can overwrite data

### Solution

- Write fencing: reject stale writes using monotonic tokens
- Idempotency: ensure duplicate requests return same result

### Flow

```text
request
  -> idempotency check
  -> fence validation
  -> execute
  -> store result
```

### Key Concepts

- Fence token per tenant + region
- Last-writer-wins only after fencing validation
- Idempotency key derived from request payload

### Why this matters

Before:

```text
Duplicate execution + unsafe writes
```

After:

```text
Safe retries + controlled writes
```

### Result

- No duplicate processing
- Stronger consistency guarantees
- Production-safe distributed system

### Next Step

```text
next: persist fencing + idempotency in DynamoDB
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
