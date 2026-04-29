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
  -> multi-tenant worker
  -> CloudWatch logs
  -> analyzer
  -> optional LLM summarizer
  -> Slack delivery
```

Current best next step:

```text
next: region-aware routing + write conflict handling
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

Document the first vertical slice: logs to worker, normalization, analyzer, summarizer, and Slack delivery.

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

Analyze normalized logs before summarization: count events, count errors/warnings, group repeated patterns, determine severity, and build evidence.

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

Convert `AnalysisResult` into a human-readable `IncidentSummary` with title, severity, summary, evidence, and next steps.

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

Deliver incident summaries to Slack, with local console fallback when no webhook is configured.

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

Document how to clone, install dependencies, run sample logs, run CloudWatch logs, configure Slack, and troubleshoot common issues.

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

Introduce optional AI-powered summarization on top of deterministic analysis.

Key design principle:

```text
The LLM receives compact analysis output, not raw logs.
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

Provide a command-line interface for running the OAAS pipeline without relying only on environment variables.

Usage:

```bash
python -m app.cli analyze
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

Add proactive observability by summarizing system behavior over a time window.

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

Deliver daily digest to Slack instead of only printing it locally.

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

Load tenants, iterate sources, read CloudWatch logs, analyze logs, summarize, and send per-tenant Slack output.

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

Improve scalability by processing tenants concurrently with `ThreadPoolExecutor`.

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
Core primitives exist, but they still need to be wired into workers/multi_tenant_worker.py or workers/sqs_worker.py.
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

Expose the observability system through HTTP API endpoints.

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

Add observability to the queue worker so OAAS can monitor its own job execution health.

Metrics emitted:

```text
JobSuccess
JobFailure
JobLatency
```

---

## Step 30 — Structured Logging + Trace Correlation

Commit:

```text
feat(logging): add structured JSON logger
feat(trace): add trace id generator
feat(api): add trace id and structured logging
feat(trace): propagate trace id through SQS worker
feat(trace): propagate trace id into tenant processing and Slack output
```

Files changed:

```text
app/core/logger.py
app/core/trace.py
app/api/main.py
workers/sqs_worker.py
workers/multi_tenant_worker.py
```

Purpose:

Enable end-to-end traceability across the distributed system.

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

---

## Step 34 — Production Hardening (IAM + Autoscaling)

Commit:

```text
infra(ecs): add least privilege IAM roles
infra(ecs): add autoscaling policies (CPU + SQS)
```

Files changed:

```text
infra/terraform/modules/ecs/iam.tf
infra/terraform/modules/ecs/autoscaling.tf
```

Purpose:

Harden the system for production by enforcing security best practices and enabling automatic scaling.

### IAM

- Separate execution role vs task role
- Restrict SQS access to specific queue ARNs
- Allow only required CloudWatch log read actions
- Allow metric publishing only

### Autoscaling

- CPU-based ECS scaling
- SQS queue-depth based scaling

---

## Step 35 — CI/CD Pipeline (GitHub Actions → ECR → ECS)

Commit:

```text
ci(deploy): add GitHub Actions ECS deployment workflow
docs: add CI/CD pipeline documentation
```

Files changed:

```text
.github/workflows/deploy-ecs.yml
docs/cicd.md
```

Purpose:

Automate build and deployment pipeline from GitHub to AWS ECS.

### Flow

```text
Git push
  -> GitHub Actions
  -> Build Docker images
  -> Push to ECR
  -> Update ECS services
```

### Features

- OIDC-based AWS auth with no static access keys
- Commit-SHA image tagging
- Rolling ECS deployment
- Separate API and worker services

---

## Step 36 — Secrets Management (AWS Secrets Manager)

Commit:

```text
feat(secrets): add AWS Secrets Manager helper
infra(secrets): add Secrets Manager resources
```

Files changed:

```text
app/core/secrets.py
infra/terraform/modules/secrets/main.tf
```

Purpose:

Secure sensitive configuration using AWS Secrets Manager while preserving local environment-variable fallback.

### Design

- Environment-first fallback for local development
- Secrets Manager in production
- JSON-based secret payloads
- IAM-controlled access
- Rotation-ready foundation

### Configuration

```bash
export ENABLE_AWS_SECRETS=true
export SLACK_SECRET_NAME=oaas-mvp-slack
export API_KEYS_SECRET_NAME=oaas-mvp-api-keys
```

---

## Step 37 — Blue/Green Deployment (ECS + CodeDeploy)

Commit:

infra(ecs): add CodeDeploy blue-green deployment group  
docs: add blue/green deployment guide  

Files:

- infra/terraform/modules/ecs/codedeploy.tf  
- docs/blue-green.md  

Purpose:

Enable zero-downtime deployments with automatic rollback.

### Design

- Blue = current version  
- Green = new version  
- Traffic shifted gradually via ALB  

### Strategy

- Canary: 10% traffic for 5 minutes  
- Full cutover after validation  

### Rollback

- Automatic on failure  
- Automatic on CloudWatch alarms  

### Result

- Zero downtime deployments  
- Safe release process  
- Fast rollback capability  

### Next Step

next: multi-region failover (Route53 + health checks)

---

## Step 38 — Multi-Region Failover (Route53 + Health Checks)

Commit:

infra(route53): add multi-region failover module  
docs(infra): add multi-region failover guide

Files:

- infra/terraform/modules/route53-failover/main.tf
- docs/multi-region-failover.md

Purpose:

Enable high availability by deploying the system across multiple AWS regions with automatic Route53 failover.

### Architecture

```text
Client
  -> Route53 Failover Policy
       -> Primary Region (ECS + ALB)
       -> Secondary Region (ECS + ALB)
```

### Implementation

- Route53 health checks for primary and secondary regional endpoints
- PRIMARY / SECONDARY failover routing policy
- Low TTL for faster failover
- `/health` endpoint used as regional health signal

### Failover Flow

1. Route53 checks the primary endpoint.
2. If primary becomes unhealthy, Route53 marks it down.
3. Traffic shifts to the secondary regional endpoint.
4. When primary recovers, traffic can return based on Route53 failover behavior.

### Why this matters

Before:

```text
Single-region deployment risk
```

After:

```text
Multi-region API failover with automatic traffic recovery
```

### Next Step

next: global data replication (DynamoDB Global Tables)

---

## Step 39 — Global Data Replication (DynamoDB Global Tables)

Commit:

infra(dynamodb): add global table module  
docs(infra): add DynamoDB global tables guide

Files:

- infra/terraform/modules/dynamodb-global/main.tf
- docs/dynamodb-global.md

Purpose:

Enable multi-region data consistency across failover regions using DynamoDB Global Tables.

### Architecture

```text
Primary Region (us-east-1)
    ↔ replication ↔
Secondary Region (us-west-2)
```

### Implementation

- DynamoDB Global Tables with replica regions
- PAY_PER_REQUEST billing mode
- Streams enabled for replication
- Point-in-time recovery enabled
- Server-side encryption enabled

### Data Model

Partition key:

```text
pk (tenant_id)
```

Sort key:

```text
sk (entity_id / job_id)
```

### Failure Behavior

1. Region A fails.
2. Route53 shifts traffic to Region B.
3. Region B reads the same replicated data.
4. System continues without data loss.

### Consistency Model

- Eventual consistency across regions
- Last-writer-wins conflict resolution
- Idempotent writes recommended

### Why this matters

Before:

```text
Multi-region compute WITHOUT shared state
```

After:

```text
Multi-region compute WITH replicated data layer
```

### Result

- True active-active architecture
- No data loss during failover
- Low-latency regional reads

### Next Step

next: region-aware routing + write conflict handling

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

---

## Runbook Rule Going Forward

For every future implementation step:

1. Make the code or documentation change.
2. Add or update the matching runbook section.
3. Use semantic commit messages.
