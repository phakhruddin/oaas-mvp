# Build Runbook

... (existing content unchanged above) ...

## Step 14 — Add LLM Summarization Layer

Commit:

```text
feat(ai): add optional LLM summarization provider
```

Files changed:

```text
app/services/llm_summarizer.py
workers/log_worker.py
```

Purpose:

Introduce an optional AI-powered summarization layer on top of the deterministic analyzer.

Key design principle:

> The LLM receives compact analysis output, NOT raw logs.

### Implementation details

- New class: `LLMSummarizer`
- Uses environment variable `OPENAI_API_KEY`
- Uses model configurable via `OPENAI_MODEL`
- Falls back to deterministic `Summarizer` if:
  - API key is not set
  - API call fails
  - dependency is missing

### Worker integration

New toggle:

```bash
export USE_LLM=true
```

Behavior:

- `USE_LLM=true` → use `LLMSummarizer`
- otherwise → use deterministic `Summarizer`

### Run examples

Local deterministic:

```bash
python workers/log_worker.py
```

LLM-enabled:

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

### Why this matters

Before this step:

```text
deterministic log analysis tool
```

After this step:

```text
AI observability assistant
```

### Risks introduced

- LLM cost
- hallucination risk

Mitigations:

- feed structured analysis, not raw logs
- include evidence in output
- fallback to deterministic summary

## Where We Are Now

The latest completed step is:

```text
next: add LLM summarization layer
```

That step is complete.

## Next Recommended Step

```text
next: add CLI interface (oaas analyze)
```

Reason:

The system is now functional but developer-driven. A CLI makes it usable as a real tool.

## Step 20 — Config Management + Multi-Env

Commit:

feat(config): add multi-environment config loader

Files:

- app/core/config.py
- config/dev.env
- config/prod.env
- config/local.env

Purpose:

Centralize configuration and support multiple environments.

### Environments

- dev
- prod
- local override

### Usage

```python
config = load_config()

## Step 21 — Multi-Tenant Architecture

Commit:

feat(tenant): add tenant configuration models

Files:

- app/models/tenant.py

Purpose:

Enable support for multiple customers (tenants) in a single system.

### Key Concepts

- Tenant = customer
- TenantLogSource = one ingestion source
- Each tenant can have:
  - multiple log sources
  - own Slack webhook
  - own AI settings

### Why this matters

Before:
single-user tool

After:
multi-tenant SaaS platform

## Step 22 — Multi-Tenant Execution

Commit:

feat(worker): add multi-tenant processing worker

Files:

- app/core/tenant_loader.py
- workers/multi_tenant_worker.py

Purpose:

Execute observability pipeline per tenant.

### Flow

- load tenants
- iterate sources
- analyze logs
- send per-tenant output

### Result

System supports multiple customers.

## Step 23 — Parallel Tenant Processing

Commit:

feat(worker): parallelize tenant processing

Files:

- workers/multi_tenant_worker.py

Purpose:

Improve scalability by processing tenants concurrently.

### Implementation

- ThreadPoolExecutor
- configurable worker count
- failure isolation

### Config

```bash
TENANT_WORKER_THREADS=4

## Step 24 — Rate Limiting + Circuit Breaker

Commit:

feat(rate-limit): add tenant rate limiter  
feat(resilience): add circuit breaker  

Files:

- app/core/rate_limiter.py  
- app/core/circuit_breaker.py  

Purpose:

Protect system from misbehaving tenants and external failures.

### Rate Limiting

- limits tenant execution frequency
- prevents overload

### Circuit Breaker

- stops repeated failures
- auto-recovers after cooldown

### Why this matters

Before:
bad tenant → system instability

After:
bad tenant → isolated + controlled

## Step 25 — FastAPI Service Layer

Commit:

feat(api): add FastAPI service layer

Files:

- app/api/main.py

Purpose:

Expose observability system via HTTP API.

### Endpoints

- GET /health
- GET /tenants
- POST /tenants/{tenant_id}/analyze

### Why this matters

Before:
CLI / worker-only system

After:
service-based architecture (SaaS foundation)

### Next Step

next: async job queue (SQS / background workers)
