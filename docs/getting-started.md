# Getting Started

This guide explains how to run the OAAS MVP locally using either sample logs or real AWS CloudWatch Logs.

## Prerequisites

- Python 3.10+
- Git
- AWS CLI configured if using CloudWatch mode
- Optional: Slack incoming webhook URL

## Clone the Repository

```bash
git clone https://github.com/phakhruddin/oaas-mvp.git
cd oaas-mvp
```

## Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Install Dependencies

The current MVP uses only the Python standard library for sample mode.

For CloudWatch mode, install `boto3`:

```bash
pip install boto3
```

## Run with Sample Logs

Sample mode is the default mode and does not require AWS or Slack.

```bash
python workers/log_worker.py
```

Expected behavior:

- Loads hardcoded sample logs
- Normalizes them into `LogEvent` objects
- Analyzes error and warning patterns
- Generates a human-readable incident summary
- Prints a Slack-style message to the console

Example output:

```text
[Worker] Loading logs...
[Worker] Source: sample logs
[Worker] Loaded 5 events
[SlackClient] No webhook configured. Printing message:

🚨 payment-service service degraded
Severity: HIGH

Processed 5 logs. Errors: 3, Warnings: 1. Affected services: checkout-service, payment-service.

Evidence:
- First error from payment-service: DB timeout
- Warnings detected: 1
- Pattern repeated 2 time(s): payment-service:error:DB timeout

Next steps:
- Check recent deployments for affected services
- Inspect logs around first error occurrence
- Check infrastructure dependencies (DB, cache, network)
```

## Run with CloudWatch Logs

CloudWatch mode reads real logs from an AWS CloudWatch log group.

### 1. Configure AWS Credentials

Use the AWS CLI or environment variables.

```bash
aws configure
```

Or:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

If using temporary credentials, also export:

```bash
export AWS_SESSION_TOKEN="your-session-token"
```

### 2. Install boto3

```bash
pip install boto3
```

### 3. Run CloudWatch Mode

```bash
export USE_CLOUDWATCH=true
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export AWS_REGION="us-east-1"

python workers/log_worker.py
```

## CloudWatch Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `USE_CLOUDWATCH` | No | `false` | Set to `true` to read from CloudWatch. |
| `CLOUDWATCH_LOG_GROUP` | Yes, if CloudWatch mode | none | CloudWatch log group name. |
| `AWS_REGION` | No | `us-east-1` | AWS region for CloudWatch Logs. |
| `CLOUDWATCH_LOOKBACK_MINUTES` | No | `15` | How far back to read logs. |
| `CLOUDWATCH_LIMIT` | No | `100` | Maximum number of log events to read. |
| `CLOUDWATCH_FILTER_PATTERN` | No | empty | Optional CloudWatch filter pattern. |
| `SERVICE_NAME` | No | inferred | Override service name in normalized events. |
| `SLACK_WEBHOOK_URL` | No | none | Send output to Slack instead of console. |

## Run with CloudWatch Filter Pattern

Example: only pull error-like logs.

```bash
export USE_CLOUDWATCH=true
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export CLOUDWATCH_FILTER_PATTERN="ERROR"
export CLOUDWATCH_LOOKBACK_MINUTES=30
export CLOUDWATCH_LIMIT=200

python workers/log_worker.py
```

## Send Output to Slack

If `SLACK_WEBHOOK_URL` is set, the worker sends the incident summary to Slack.

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx/yyy/zzz"
python workers/log_worker.py
```

CloudWatch + Slack example:

```bash
export USE_CLOUDWATCH=true
export CLOUDWATCH_LOG_GROUP="/aws/lambda/payment-service"
export AWS_REGION="us-east-1"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx/yyy/zzz"

python workers/log_worker.py
```

## How the Local Pipeline Works

```text
Log source
  -> LogEvent normalization
  -> LogAnalyzer
  -> Summarizer
  -> SlackClient
  -> Slack or console output
```

## Troubleshooting

### ModuleNotFoundError: No module named 'app'

Run the command from the repository root:

```bash
python workers/log_worker.py
```

If needed, set `PYTHONPATH` manually:

```bash
export PYTHONPATH=$(pwd)
python workers/log_worker.py
```

### boto3 is required for CloudWatch integration

Install boto3:

```bash
pip install boto3
```

### CLOUDWATCH_LOG_GROUP is required

When `USE_CLOUDWATCH=true`, this variable must be set:

```bash
export CLOUDWATCH_LOG_GROUP="/aws/lambda/your-service"
```

### AWS credential errors

Verify the active identity:

```bash
aws sts get-caller-identity
```

Verify CloudWatch permissions include:

- `logs:FilterLogEvents`
- `logs:DescribeLogGroups`
- `logs:DescribeLogStreams`

## Next Recommended Improvements

- Add `requirements.txt`
- Add CLI arguments instead of environment variables only
- Add CloudWatch pagination support
- Add unit tests for analyzer and summarizer
- Add LLM-powered summarization layer
