# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

Use this file as the companion operational record for every major implementation step in the repo.

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

## Step 1 — Create Repo Foundation

Commit:

```text
first commit
```

Files changed:

```text
README.md
```

Purpose:

Create the initial GitHub repository for the Observability-as-a-Service MVP.

---

## Step 2 — Expand README

Commit:

```text
docs: expand observability service MVP overview
```

Files changed:

```text
README.md
```

Purpose:

Document the product idea, customer segment, problem, MVP scope, architecture, pricing direction, and first-build milestone.

---

## Step 3 — Create Repo Structure

Commit:

```text
feat(initial): placeholder
```

Files changed:

```text
app/
workers/
integrations/
infra/
docs/
tests/
scripts/
```

Purpose:

Create the initial project layout for the Python service, integrations, docs, infrastructure, and tests.

---

## Step 4 — Add Architecture Doc

Commit:

```text
docs(architecture): add MVP system design
```

Files changed:

```text
docs/architecture.md
```

Purpose:

Document the first vertical slice:

```text
CloudWatch Logs / sample logs
  -> Log worker
  -> LogEvent model normalization
  -> Analyzer service
  -> Summarizer service
  -> Slack client
```

Key principle:

```text
Do deterministic analysis before AI summarization. Do not send raw high-volume logs directly to an LLM.
```

---

## Step 5 — Add MVP Roadmap

Commit:

```text
docs(roadmap): add MVP execution plan
```

Files changed:

```text
docs/mvp-roadmap.md
```

Purpose:

Track phased delivery from local demo pipeline to Slack integration, CloudWatch input, AI summarization, and daily digest.

---

## Step 6 — Add LogEvent Model

Commit:

```text
feat(model): add LogEvent data structure
```

Files changed:

```text
app/models/log_event.py
```

Purpose:

Create the normalized domain object used across the pipeline.

Core fields:

- `timestamp`
- `service`
- `level`
- `message`
- `source`
- `metadata`

Helper methods:

- `is_error()`
- `is_warning()`
- `summary_key()`

---

## Step 7 — Add Analyzer

Commit:

```text
feat(analyzer): implement basic log analysis logic
```

Files changed:

```text
app/services/analyzer.py
```

Purpose:

Analyze normalized logs before summarization.

Responsibilities:

- Count events
- Count errors and warnings
- Count events by service
- Count events by level
- Group repeated patterns
- Determine severity
- Build evidence for the summary

---

## Step 8 — Add Summarizer

Commit:

```text
feat(summarizer): generate human-readable incident summary
```

Files changed:

```text
app/services/summarizer.py
```

Purpose:

Convert `AnalysisResult` into a human-readable `IncidentSummary`.

Output includes:

- title
- severity
- summary
- evidence
- next steps

---

## Step 9 — Add Slack Client

Commit:

```text
feat(slack): add Slack notification client
```

Files changed:

```text
integrations/slack/slack_client.py
```

Purpose:

Deliver incident summaries.

Behavior:

- If `SLACK_WEBHOOK_URL` is set, send to Slack webhook.
- If not set, print message locally for development.

---

## Step 10 — Add Local Worker Pipeline

Commit:

```text
feat(worker): implement log processing pipeline
```

Files changed:

```text
workers/log_worker.py
```

Purpose:

Wire sample logs through the full local MVP pipeline.

Run command:

```bash
python workers/log_worker.py
```

---

## Step 11 — Add CloudWatch Reader

Commit:

```text
feat(cloudwatch): add CloudWatch log reader
```

Files changed:

```text
integrations/aws/cloudwatch.py
```

Purpose:

Read real CloudWatch log events and convert them into `LogEvent` objects.

Capabilities:

- Uses `boto3`
- Reads recent log events from a configured log group
- Infers service name from log group name
- Infers level from message contents
- Preserves CloudWatch metadata

---

## Step 12 — Wire CloudWatch Into Worker

Commit:

```text
feat(worker): wire CloudWatch log source toggle
```

Files changed:

```text
workers/log_worker.py
```

Purpose:

Allow the worker to run in either local sample mode or CloudWatch mode.

Sample mode:

```bash
python workers/log_worker.py
```

CloudWatch mode:

```bash
export USE_CLOUDWATCH=true
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export AWS_REGION="us-east-1"
python workers/log_worker.py
```

---

## Step 13 — Add Getting Started Runbook

Commit:

```text
docs(runbook): add local and CloudWatch execution steps
```

Files changed:

```text
docs/getting-started.md
```

Purpose:

Document how to run the MVP locally and with CloudWatch.

Covers:

- Clone repo
- Create virtual environment
- Install `boto3`
- Run with sample logs
- Run with CloudWatch logs
- Configure Slack webhook
- Troubleshooting

---

## Step 14 — Add LLM Summarization Layer

Commit:

```text
feat(ai): add optional LLM summarization provider
feat(worker): add LLM summarization toggle
```

Files changed:

```text
app/services/llm_summarizer.py
workers/log_worker.py
```

Purpose:

Introduce an optional AI-powered summarization layer on top of the deterministic analyzer.

Key design principle:

```text
The LLM receives compact analysis output, not raw logs.
```

Run examples:

```bash
export USE_LLM=true
export OPENAI_API_KEY="your-key"
python workers/log_worker.py
```

CloudWatch + LLM:

```bash
export USE_CLOUDWATCH=true
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export USE_LLM=true
export OPENAI_API_KEY="your-key"
python workers/log_worker.py
```

---

## Step 15 — Add CLI Interface

Commit:

```text
refactor(worker): expose reusable pipeline function
feat(cli): add oaas analyze command
```

Files changed:

```text
app/cli.py
workers/log_worker.py
```

Purpose:

Provide a user-friendly command-line interface for running the OAAS pipeline without relying only on environment variables.

Usage:

```bash
python -m app.cli analyze
```

CloudWatch example:

```bash
python -m app.cli analyze \
  --source cloudwatch \
  --log-group "/aws/lambda/payment-service" \
  --minutes 30 \
  --limit 200
```

LLM example:

```bash
python -m app.cli analyze --use-llm
```

---

## Step 16 — Add CloudWatch Pagination

Commit:

```text
feat(cloudwatch): add paginated log retrieval
```

Files changed:

```text
integrations/aws/cloudwatch.py
```

Purpose:

Read more than one page of CloudWatch logs using `nextToken` instead of a single `filter_log_events` call.

Behavior:

- Continue until `limit` is reached.
- Stop when CloudWatch returns no `nextToken`.
- Convert each result into `LogEvent`.

---

## Step 17 — Add Daily Digest Job

Commit:

```text
feat(digest): add daily digest service
feat(worker): add daily digest worker
```

Files changed:

```text
app/services/digest.py
workers/digest_worker.py
```

Purpose:

Add a proactive observability feature that summarizes system behavior over a time window.

Run command:

```bash
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export AWS_REGION="us-east-1"
python workers/digest_worker.py
```

---

## Step 18 — Schedule Daily Digest

Commit:

```text
ci(digest): schedule daily digest workflow
```

Files changed:

```text
.github/workflows/daily-digest.yml
```

Purpose:

Run the daily digest automatically through GitHub Actions.

Schedule:

```text
0 14 * * *
```

Meaning:

```text
Run daily at 14:00 UTC.
```

---

## Step 19 — Send Digest to Slack

Commit:

```text
feat(digest): send daily digest to Slack
```

Files changed:

```text
workers/digest_worker.py
```

Purpose:

Deliver the daily digest to Slack instead of only printing it locally.

Important follow-up:

```text
SlackClient needs a send_text() helper for raw text payloads.
```

---

## Step 20 — Add Retry + Backoff Helper

Commit:

```text
feat(retry): add exponential backoff helper
```

Files changed:

```text
app/core/retry.py
```

Purpose:

Add reusable exponential backoff with jitter for external calls.

Intended usage:

- CloudWatch API calls
- Slack webhook calls
- future external integrations

---

## Step 21 — Config Management + Multi-Env

Commit:

```text
feat(config): add multi-environment config loader
```

Files changed / intended:

```text
app/core/config.py
config/dev.env
config/prod.env
config/local.env
```

Purpose:

Centralize configuration and support multiple environments.

Status:

```text
Needs verification because the earlier GitHub write failed for app/core/config.py.
```

---

## Step 22 — Multi-Tenant Architecture

Commit:

```text
feat(tenant): add tenant configuration models
```

Files changed:

```text
app/models/tenant.py
```

Purpose:

Enable support for multiple customers in a single system.

Key concepts:

- Tenant = customer
- TenantLogSource = one ingestion source
- Each tenant can have multiple log sources, Slack configuration, and AI settings.

---

## Step 23 — Tenant Loader + Multi-Tenant Worker

Commit:

```text
feat(tenant): add tenant config loader
feat(worker): add multi-tenant processing worker
```

Files changed:

```text
app/core/tenant_loader.py
workers/multi_tenant_worker.py
```

Purpose:

Execute the observability pipeline per tenant.

Flow:

```text
load tenants
  -> iterate tenant sources
  -> read CloudWatch logs
  -> analyze logs
  -> summarize
  -> send per-tenant Slack output
```

---

## Step 24 — Parallel Tenant Processing

Commit:

```text
feat(worker): parallelize tenant processing
```

Files changed:

```text
workers/multi_tenant_worker.py
```

Purpose:

Improve scalability by processing tenants concurrently.

Implementation:

- `ThreadPoolExecutor`
- configurable worker count
- failure isolation

Config:

```bash
export TENANT_WORKER_THREADS=4
```

---

## Step 25 — Rate Limiting + Circuit Breaker

Commit:

```text
feat(rate-limit): add tenant rate limiter
feat(resilience): add circuit breaker
```

Files changed:

```text
app/core/rate_limiter.py
app/core/circuit_breaker.py
```

Purpose:

Protect the system from misbehaving tenants and repeated external failures.

Status:

```text
Core primitives exist, but they still need to be wired into workers/multi_tenant_worker.py.
```

---

## Step 26 — FastAPI Service Layer

Commit:

```text
feat(api): add FastAPI service layer
```

Files changed:

```text
app/api/main.py
```

Purpose:

Expose the observability system through an HTTP API.

Endpoints:

- `GET /health`
- `GET /tenants`
- `POST /tenants/{tenant_id}/analyze`

Why this matters:

```text
Before: CLI / worker-only system
After: service-based SaaS foundation
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
```

---

## Known Follow-Ups

1. Add structured logging and trace correlation.
2. Wire rate limiter and circuit breaker into `workers/sqs_worker.py`.
3. Add DLQ replay tooling.
4. Add tests for queue failure paths.
5. Add CloudWatch dashboard definitions for queue metrics.
6. Add `send_text()` to `integrations/slack/slack_client.py` if not already present.
7. Verify `app/core/config.py` exists and is populated.
8. Add `config/tenants.example.json` so tenant setup is documented safely without secrets.
9. Update `.github/workflows/daily-digest.yml` to pass `SLACK_WEBHOOK_URL` if not already present.
10. Add `requirements.txt` with required packages.

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code or documentation change.
2. Add or update the matching runbook section.
3. Use semantic commit messages.

Examples:

```text
feat(queue): add SQS job publisher
docs(runbook): document queue worker architecture

fix(slack): add raw text sender for digest
docs(runbook): document digest Slack delivery
```
