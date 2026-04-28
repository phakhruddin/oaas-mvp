# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

## Current Status

```text
FastAPI API
  -> SQS queue
  -> SQS worker
  -> DLQ handling
  -> multi-tenant worker
  -> CloudWatch
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: metrics + observability for queue system
```

---

## Step 27 — Async Job Queue (SQS Workers)

Commit:

```text
feat(queue): add analysis job model
feat(queue): add SQS client abstraction
feat(api): enqueue tenant analysis jobs
feat(worker): add SQS queue worker
```

Files changed:

```text
app/models/job.py
integrations/aws/sqs_client.py
app/api/main.py
workers/sqs_worker.py
```

Purpose:

Decouple API requests from tenant processing by placing analysis work onto a queue.

Architecture:

```text
FastAPI -> SQS -> sqs_worker.py -> process_tenant -> Slack
```

Run worker:

```bash
python workers/sqs_worker.py
```

API response after enqueue:

```json
{
  "tenant_id": "acme",
  "job_type": "analyze",
  "status": "queued"
}
```

---

## Step 28 — DLQ + Failure Handling

Commit:

```text
feat(queue): add DLQ support to SQS client
feat(queue): add DLQ handling in worker
```

Files changed:

```text
integrations/aws/sqs_client.py
workers/sqs_worker.py
```

Purpose:

Handle failed queue jobs safely without leaving poisoned messages in the main queue.

Success path:

```text
receive message -> process tenant -> delete from main queue
```

Failure path:

```text
receive message -> processing fails -> send to DLQ -> delete from main queue
```

Environment variables:

```text
SQS_QUEUE_URL
SQS_DLQ_URL
```

Why this matters:

```text
prevents infinite retry loops
keeps the main queue healthy
preserves failed job context for investigation
```

---

## Known Follow-Ups

1. Add metrics for job success, failure, and latency
2. Add structured logging
3. Wire rate limiter and circuit breaker into sqs_worker
4. Add DLQ replay tooling
5. Add tests for queue failure paths

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code change
2. Update this runbook
3. Use semantic commits
