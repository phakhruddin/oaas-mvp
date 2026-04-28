import os
from datetime import datetime
from typing import List

from app.models.log_event import LogEvent
from app.services.analyzer import LogAnalyzer
from app.services.summarizer import Summarizer
from integrations.aws.cloudwatch import CloudWatchLogReader
from integrations.slack.slack_client import SlackClient


def load_sample_logs() -> List[LogEvent]:
    return [
        LogEvent(datetime.utcnow(), "payment-service", "error", "DB timeout"),
        LogEvent(datetime.utcnow(), "payment-service", "error", "DB timeout"),
        LogEvent(datetime.utcnow(), "payment-service", "warn", "Retrying connection"),
        LogEvent(datetime.utcnow(), "checkout-service", "info", "Request received"),
        LogEvent(datetime.utcnow(), "checkout-service", "error", "Null pointer exception"),
    ]


def load_cloudwatch_logs() -> List[LogEvent]:
    log_group_name = os.getenv("CLOUDWATCH_LOG_GROUP")

    if not log_group_name:
        raise ValueError("CLOUDWATCH_LOG_GROUP is required when USE_CLOUDWATCH=true")

    minutes = int(os.getenv("CLOUDWATCH_LOOKBACK_MINUTES", "15"))
    limit = int(os.getenv("CLOUDWATCH_LIMIT", "100"))
    filter_pattern = os.getenv("CLOUDWATCH_FILTER_PATTERN", "")
    service_name = os.getenv("SERVICE_NAME")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    reader = CloudWatchLogReader(region_name=aws_region)

    return reader.read_recent_events(
        log_group_name=log_group_name,
        minutes=minutes,
        filter_pattern=filter_pattern,
        limit=limit,
        service_name=service_name,
    )


def load_events() -> List[LogEvent]:
    use_cloudwatch = os.getenv("USE_CLOUDWATCH", "false").lower() == "true"

    if use_cloudwatch:
        print("[Worker] Source: CloudWatch Logs")
        return load_cloudwatch_logs()

    print("[Worker] Source: sample logs")
    return load_sample_logs()


def main():
    print("[Worker] Loading logs...")
    events = load_events()

    print(f"[Worker] Loaded {len(events)} events")

    analyzer = LogAnalyzer()
    result = analyzer.analyze(events)

    summarizer = Summarizer()
    summary = summarizer.summarize(result)

    slack = SlackClient()
    slack.send(summary)


if __name__ == "__main__":
    main()
