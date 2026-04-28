# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

## Current Status

```text
FastAPI API
  -> SQS queue
  -> SQS worker
  -> DLQ handling
  -> CloudWatch metrics
  -> multi-tenant worker
  -> CloudWatch logs
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: structured logging + trace correlation
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

## Step 29 — Metrics + Observability for Queue System

Commit:

```text
feat(metrics): add CloudWatch metrics client
feat(metrics): instrument SQS worker with metrics
```

Files changed:

```text
integrations/aws/cloudwatch_metrics.py
workers/sqs_worker.py
```

Purpose:

Add observability to the queue worker so the OAAS system can monitor its own job execution health.

Metrics emitted:

```text
JobSuccess
JobFailure
JobLatency
```

Metric dimensions:

```text
tenant_id
```

Local mode:

```text
If ENABLE_CLOUDWATCH_METRICS=false, metrics are printed locally instead of sent to CloudWatch.
```

CloudWatch mode:

```bash
export ENABLE_CLOUDWATCH_METRICS=true
export AWS_REGION=us-east-1
export METRICS_NAMESPACE="OAAS/MVP"
python workers/sqs_worker.py
```

Why this matters:

```text
The observability platform can now observe itself.
This enables success-rate tracking, failure tracking, latency visibility, and per-tenant operational insight.
```

---

## Known Follow-Ups

1. Add structured logging and trace correlation
2. Wire rate limiter and circuit breaker into sqs_worker
3. Add DLQ replay tooling
4. Add tests for queue failure paths
5. Add CloudWatch dashboard definitions for queue metrics

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code change
2. Update this runbook
3. Use semantic commits
