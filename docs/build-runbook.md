# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

Use this file as the companion operational record for every major implementation step in the repo.

## Current Status

The project is currently at:

```text
FastAPI API
  -> SQS queue (job dispatch)
  -> multi-tenant worker (parallel)
  -> CloudWatch log sources
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: DLQ + failure handling
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

Decouple API from worker execution using asynchronous job queue.

---

### Architecture

```text
FastAPI
   -> enqueue job (SQS)
SQS Queue
   -> message buffer
Worker (sqs_worker.py)
   -> consume job
   -> process tenant
   -> send results to Slack
```

---

### Behavior

#### Before

```text
API request blocks until tenant processing completes
```

#### After

```text
API returns immediately (job queued)
Worker processes job asynchronously
```

---

### Local Development Mode

If `SQS_QUEUE_URL` is not set:

```text
- messages are printed instead of sent
- system still works without AWS
```

---

### Worker Execution

Run worker locally:

```bash
python workers/sqs_worker.py
```

---

### API Behavior

```http
POST /tenants/{tenant_id}/analyze
```

Response:

```json
{
  "tenant_id": "acme",
  "job_type": "analyze",
  "status": "queued"
}
```

---

### Why this matters

```text
Transforms system from synchronous service
into distributed, scalable architecture
```

---

## Known Follow-Ups

1. Add Dead Letter Queue (DLQ) for failed jobs
2. Add visibility timeout + retry strategy
3. Wire rate limiter + circuit breaker into sqs_worker
4. Add metrics (job success / failure / latency)
5. Add structured logging

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code change
2. Update runbook
3. Use semantic commits
