# Architecture

## Goal

Build a small, useful vertical slice for an AI-powered Observability-as-a-Service MVP.

The first version should answer one question well:

> What happened in my logs, how severe is it, and what should I check first?

## MVP Flow

```text
CloudWatch Logs / sample logs
        |
        v
Log worker
        |
        v
LogEvent model normalization
        |
        v
Analyzer service
        |
        v
Summarizer service
        |
        v
Slack client
```

## Components

### 1. Log Source

Initial source options:

- Local sample logs for development
- AWS CloudWatch Logs for first real integration
- Kubernetes logs later through Fluent Bit, Vector, or OpenTelemetry Collector

For the first working slice, local sample logs are enough. This allows the product logic to be validated before adding AWS permissions, pagination, throttling, and retry complexity.

### 2. Log Worker

The worker coordinates the pipeline:

1. Load raw log lines
2. Convert them into normalized `LogEvent` objects
3. Send events into the analyzer
4. Send analyzer output into the summarizer
5. Send the final summary to Slack-style output

The worker should stay thin. It orchestrates but does not own business logic.

### 3. LogEvent Model

The `LogEvent` model provides a consistent shape for logs.

Important fields:

- `timestamp`
- `service`
- `level`
- `message`
- `source`
- `metadata`

This keeps the analyzer independent from CloudWatch, Kubernetes, or local sample input formats.

### 4. Analyzer Service

The analyzer should perform deterministic analysis first.

Initial responsibilities:

- Count logs by severity
- Count logs by service
- Detect error keywords
- Group similar messages
- Assign a basic severity
- Produce evidence for the summarizer

Important principle:

> Do not send raw high-volume logs directly to an LLM.

The analyzer reduces noise before any AI summarization happens.

### 5. Summarizer Service

The summarizer turns analyzer output into a human-readable incident summary.

For early MVP work, it can be rule-based and deterministic.

Later, this layer can call an LLM provider, but the interface should remain stable.

Expected output:

- Title
- Severity
- Summary
- Evidence
- Suggested next checks

### 6. Slack Client

The Slack client should be isolated from business logic.

Initial MVP behavior:

- Format an incident message
- Print locally if no webhook exists
- Post to Slack webhook when configured

This makes local testing easy without requiring Slack credentials.

## Data Flow Contract

```text
Raw log line
  -> LogEvent
  -> AnalysisResult
  -> IncidentSummary
  -> Slack message
```

## Local Development First

The first implementation should run without cloud dependencies.

Example:

```bash
python workers/log_worker.py
```

Expected behavior:

- Load sample logs from inside the worker or a future sample file
- Analyze them
- Print a Slack-style incident summary

## Future Architecture

```text
CloudWatch Logs
      |
      v
Ingestion API / scheduled puller
      |
      v
Queue: SQS / Kinesis / Kafka
      |
      v
Worker fleet
      |
      v
Storage: S3 + ClickHouse/Postgres
      |
      v
Analyzer + AI summarizer
      |
      v
Slack / Email / Dashboard
```

## Design Principles

- Keep ingestion separate from analysis
- Keep AI summarization separate from deterministic detection
- Show evidence for every recommendation
- Prefer Slack-first delivery for MVP
- Avoid dashboard-heavy UX early
- Optimize for signal, not raw log volume

## First Production Milestone

The first production milestone is:

> CloudWatch log group -> analyzer -> summary -> Slack notification

This proves the product value before building a full platform.
