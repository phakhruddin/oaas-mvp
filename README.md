# OAAS MVP — AI-Powered Observability Service

**OAAS** stands for **Observability-as-a-Service**.

This repo captures the MVP plan for an **AI-powered log analysis and alerting service for SMBs**.

The goal is simple:

> Help small and mid-sized engineering teams understand what is happening in their systems without needing a full SRE team or an expensive enterprise observability platform.

## Positioning

**AI DevOps assistant that explains your logs — no dashboards, just answers.**

Instead of forcing SMB teams to stare at dashboards, build queries, and manually correlate logs, this service summarizes issues, groups noisy alerts, and sends actionable insights through Slack or email.

## Problem

SMB engineering teams often have:

- Logs spread across CloudWatch, Kubernetes, containers, and application services
- Too many alerts and not enough signal
- Limited DevOps/SRE staffing
- Expensive or overly complex observability tooling
- Slow root cause analysis during production incidents

The pain is not just collecting logs. The real pain is answering:

- What changed?
- What broke?
- Is this incident important?
- What should I check first?
- Can I get a plain-English summary instead of reading thousands of log lines?

## Target Customers

Initial customer profile:

- SMB SaaS companies with 5–50 engineers
- DevOps-light teams without dedicated SRE coverage
- Agencies managing multiple client applications
- Shopify/eCommerce backend teams
- Small platform teams running AWS or Kubernetes workloads

## MVP Scope

Start narrow and useful.

### MVP v1

- AWS CloudWatch log ingestion
- Basic Kubernetes/container log support later
- Log pattern grouping
- AI-powered daily incident summary
- Smart alert deduplication
- Slack notification delivery
- Email digest delivery
- Simple evidence-based root cause suggestion

### Non-goals for v1

- Full Datadog/New Relic replacement
- Complex dashboard builder
- Multi-cloud support on day one
- Long-term metrics platform
- Full SIEM/security analytics

## Core Features

### 1. AI Log Summarization

Convert high-volume logs into short, readable incident summaries.

```text
Checkout API error rate increased from 0.3% to 8.7% between 10:05–10:17 UTC.
Most failures are DB connection timeout errors from payment-service.
Likely first check: database connection pool saturation.
```

### 2. Alert Noise Reduction

Group repeated errors into a single actionable incident.

Instead of sending 500 alerts, send one useful summary.

### 3. Root Cause Suggestion

Provide likely cause with supporting evidence.

The system should not pretend to be 100% certain. It should show:

- Confidence level
- Key log patterns
- Time window
- Affected services
- Suggested next checks

### 4. Slack-First Workflow

Slack is the primary MVP interface.

```text
🚨 Incident: Payment API degraded
Severity: High
Window: 10:05–10:17 UTC
Likely cause: DB connection pool exhaustion
Evidence: 1,284 timeout logs from payment-service
Next check: DB max connections, connection pool size, recent deploys
```

### 5. Daily Digest

A daily summary for founders, engineering managers, or small platform teams.

```text
Yesterday's Observability Summary

- 3 incidents detected
- 1 customer-impacting issue
- Checkout latency increased 120%
- Most noisy service: payment-service
- Recommended action: tune DB connection pool and add timeout alert
```

## High-Level Architecture

```text
[CloudWatch Logs / App Logs / K8s Logs]
              |
              v
       [Collector Layer]
              |
              v
     [Normalization Pipeline]
              |
              v
   [Pattern Grouping + Anomaly Detection]
              |
              v
        [AI Analysis Layer]
              |
              v
       [Incident Engine]
              |
              v
 [Slack Alerts / Email Digest / API / UI]
```

## Suggested Tech Stack

### Ingestion

- AWS CloudWatch Logs
- OpenTelemetry Collector
- Fluent Bit or Vector for future agent-based ingestion

### Processing

- Python
- FastAPI
- Background workers
- Kinesis, Kafka, Redis Streams, or SQS depending on MVP size

### Storage

- S3 for raw/archive logs
- ClickHouse for searchable event storage
- PostgreSQL for app metadata and incidents

### AI Layer

- LLM API for summarization and explanation
- Classical ML/statistics for anomaly detection and clustering
- Pre-filtering before sending data to LLM to control cost

### Delivery

- Slack bot/webhook
- Email digest
- Lightweight web dashboard later

## Business Model

Possible pricing:

- Free tier: limited log volume + daily summary
- Starter: $29/month per service
- Growth: $99/month per team/workspace
- Pro: higher log volume, more integrations, longer retention
- Add-on: deep AI root cause analysis or compliance reports

SMBs usually prefer predictable pricing over surprise usage bills.

## Differentiation

Enterprise observability tools focus on large teams, dashboards, and full telemetry platforms.

OAAS should focus on:

- Simplicity
- Plain-English answers
- Slack-first workflow
- Low setup effort
- Predictable pricing
- SMB-friendly UX

## Key Risks

### LLM Cost

Logs are high-volume. Sending raw logs directly to an LLM is too expensive.

Mitigation:

- Cluster logs first
- Sample intelligently
- Send only representative examples
- Use rule-based filters before AI analysis

### Trust

Users may not trust AI-generated root cause suggestions.

Mitigation:

- Show evidence
- Include confidence score
- Link to raw logs
- Explain why the suggestion was made

### Competition

Large players already exist: Datadog, New Relic, Dynatrace, Splunk, Grafana Cloud, Honeycomb, and others.

Mitigation:

- Do not compete feature-for-feature
- Focus on SMB simplicity
- Solve one painful workflow extremely well

## Suggested First Build

The fastest useful MVP:

1. CloudWatch log connector
2. Scheduled log pull for one AWS account/log group
3. Pattern grouping
4. LLM summary
5. Slack daily digest
6. Smart alert when error volume spikes

## Repo Structure

```text
.
├── README.md
└── docs/
    ├── business-canvas.md
    ├── architecture.md
    ├── mvp-roadmap.md
    ├── pricing.md
    └── risks.md
```

## Project Status

Planning / MVP design phase.

Next step: implement the first vertical slice:

> CloudWatch Logs → pattern grouping → AI summary → Slack notification
