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

(unchanged steps 1–39)

---

## Step 40 — Region-Aware Routing + Write Conflict Handling

Commit:

feat(region): add region-aware routing and conflict resolver  
docs(region): add region routing and conflict handling guide

Files:

- app/core/region_routing.py
- docs/region-routing.md

Purpose:

Control write routing across regions and handle conflicts in a multi-region active-active system.

### Architecture

```text
Client
  -> Route53
       -> Region A / Region B
            -> RegionRouter decides operation routing
            -> DynamoDB Global Tables
            -> ConflictResolver ensures consistency
```

### Routing Strategy

- Reads → local region (low latency)
- Writes → primary write region (reduce conflicts)

### Conflict Strategy

- Last-writer-wins
- Timestamp-based resolution
- Region tagging (updated_by_region)

### Record Design

```json
{
  "updated_at": "timestamp",
  "updated_by_region": "region"
}
```

### Failure Behavior

- If writes occur in both regions
- ConflictResolver selects latest version

### Why this matters

Before:

```text
Multi-region writes = conflict risk
```

After:

```text
Controlled writes + deterministic conflict resolution
```

### Result

- Reduced write conflicts
- Predictable behavior
- Foundation for advanced routing

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
