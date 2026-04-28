# Build Runbook

This runbook tracks the step-by-step build history of the OAAS MVP.

Use this file as the companion operational record for every major implementation step in the repo.

## Current Status

The project is currently at:

```text
CloudWatch Logs / sample logs
  -> LogEvent normalization
  -> LogAnalyzer
  -> Summarizer
  -> SlackClient
  -> Console or Slack output
```

The latest completed implementation step is:

```text
feat(worker): wire CloudWatch log source toggle
```

A getting-started runbook was also added:

```text
docs(runbook): add local and CloudWatch execution steps
```

## Step 1 — Create Repo Foundation

Goal:

Create a fresh GitHub repo for the Observability-as-a-Service MVP.

Repo:

```text
phakhruddin/oaas-mvp
```

Initial state:

- Public repository
- Default branch: `main`
- README initially minimal

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

Document the business and technical direction for the AI-powered observability MVP.

The README now includes:

- Product positioning
- Target customer profile
- Core problem statement
- MVP scope
- Non-goals
- High-level architecture
- Suggested tech stack
- Business model
- Risks
- First build milestone

## Step 3 — Create Repo Structure

Commit:

```text
feat(initial): placeholder
```

Created structure:

```text
app/
  api/
  core/
  models/
  services/
workers/
integrations/
  aws/
  slack/
  email/
infra/
  terraform/
  docker/
docs/
tests/
scripts/
```

Purpose:

Create a clean project layout for a future production-grade Python service.

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

Key design decision:

Do deterministic analysis before AI summarization. Do not send raw high-volume logs directly to an LLM.

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

Track phased delivery:

- Phase 0: repo foundation
- Phase 1: local demo pipeline
- Phase 2: Slack integration
- Phase 3: CloudWatch input
- Phase 4: AI summarization
- Phase 5: daily digest

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

Flow:

```text
sample logs
  -> LogAnalyzer
  -> Summarizer
  -> SlackClient
```

Run command:

```bash
python workers/log_worker.py
```

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

Supported environment variables:

- `USE_CLOUDWATCH`
- `CLOUDWATCH_LOG_GROUP`
- `AWS_REGION`
- `CLOUDWATCH_LOOKBACK_MINUTES`
- `CLOUDWATCH_LIMIT`
- `CLOUDWATCH_FILTER_PATTERN`
- `SERVICE_NAME`

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

## Runbook Rule Going Forward

For every future implementation step, add or update a companion runbook entry.

Recommended pattern:

1. Make code or doc change.
2. Add a matching section to this file.
3. Use semantic commit messages.

Examples:

```text
feat(ai): add LLM summarization provider
docs(runbook): document LLM summarization setup

feat(cli): add analyze command
docs(runbook): document CLI usage

fix(cloudwatch): handle paginated log results
docs(runbook): document CloudWatch pagination behavior
```

## Where We Were Last

The last completed product step was:

```text
next: wire cloudwatch into worker
```

That step is complete.

Current best next step:

```text
next: add LLM summarization layer
```

Reason:

The MVP already has a working deterministic log pipeline. Adding an LLM layer turns it from a log analysis tool into an AI observability assistant.
