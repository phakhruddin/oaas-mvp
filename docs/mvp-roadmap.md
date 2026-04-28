# MVP Roadmap

## Goal

Ship a small but useful vertical slice that proves the core OAAS value:

> Logs -> analysis -> summary -> Slack-style notification

The MVP should not try to replace Datadog, Splunk, New Relic, or Grafana Cloud. The first version should prove that a small team can receive useful incident context without building dashboards or hiring a full SRE team.

## Phase 0 — Repo Foundation

Status: in progress

Deliverables:

- Repo structure
- README with product positioning
- Architecture document
- Placeholder files for product modules

Success criteria:

- A new contributor can understand the product direction in under 10 minutes.

## Phase 1 — Local Demo Pipeline

Goal:

Run the full pipeline locally without AWS, Slack, or LLM dependencies.

Deliverables:

- `LogEvent` model
- Deterministic analyzer
- Rule-based summarizer
- Console-based Slack fallback
- Worker with sample logs

Success criteria:

```bash
python workers/log_worker.py
```

Expected result:

- Prints a Slack-style incident summary
- Shows severity
- Shows affected services
- Shows evidence
- Shows suggested next checks

## Phase 2 — Slack Webhook Integration

Goal:

Send incident summaries to Slack when a webhook URL is configured.

Deliverables:

- `SLACK_WEBHOOK_URL` environment variable support
- JSON payload formatting
- Console fallback when webhook is missing
- Basic error handling for failed sends

Success criteria:

- Local run prints to console when webhook is absent
- Local run posts to Slack when webhook is present

## Phase 3 — CloudWatch Input

Goal:

Connect the local pipeline to real AWS CloudWatch Logs.

Deliverables:

- CloudWatch log group reader
- Time-window filtering
- Pagination support
- Basic AWS credential handling through standard AWS SDK behavior

Success criteria:

- Pull logs from one configured log group
- Feed logs into the same analyzer and summarizer

## Phase 4 — AI Summarization

Goal:

Add optional LLM summarization after deterministic analysis.

Deliverables:

- Provider interface for AI summarization
- Prompt template for incident explanation
- Cost guardrails through sampling and grouping
- Fallback to rule-based summary if AI is unavailable

Success criteria:

- AI receives compact analysis, not raw log streams
- Summary includes evidence and confidence language

## Phase 5 — Daily Digest

Goal:

Provide a daily operational summary for SMB teams.

Deliverables:

- Digest generation
- Incident count
- Noisiest service
- Top error patterns
- Recommended follow-up actions

Success criteria:

- A daily digest can be generated from a batch of events

## Initial Backlog

- Add sample log fixture file
- Add unit tests for analyzer
- Add unit tests for summarizer
- Add GitHub Actions test workflow
- Add Dockerfile for local execution
- Add Terraform skeleton for future AWS deployment

## Non-Goals for Early MVP

- Full metrics backend
- Long-term retention product
- Multi-tenant billing system
- Complex dashboards
- Full SIEM/security analytics
- Multi-cloud ingestion

## North Star Metric

The MVP is successful if a user can say:

> I understood the incident faster because OAAS summarized my logs and gave me the first useful thing to check.
