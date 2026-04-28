import os
from datetime import datetime
from typing import List, Optional

from app.models.log_event import LogEvent
from app.services.analyzer import LogAnalyzer
from app.services.summarizer import Summarizer
from app.services.llm_summarizer import LLMSummarizer
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


def load_cloudwatch_logs(
    log_group_name: Optional[str] = None,
    minutes: Optional[int] = None,
    limit: Optional[int] = None,
    filter_pattern: Optional[str] = None,
    service_name: Optional[str] = None,
    aws_region: Optional[str] = None,
) -> List[LogEvent]:
    resolved_log_group = log_group_name or os.getenv("CLOUDWATCH_LOG_GROUP")

    if not resolved_log_group:
        raise ValueError("CLOUDWATCH_LOG_GROUP is required when using CloudWatch logs")

    resolved_minutes = minutes or int(os.getenv("CLOUDWATCH_LOOKBACK_MINUTES", "15"))
    resolved_limit = limit or int(os.getenv("CLOUDWATCH_LIMIT", "100"))
    resolved_filter_pattern = filter_pattern if filter_pattern is not None else os.getenv("CLOUDWATCH_FILTER_PATTERN", "")
    resolved_service_name = service_name or os.getenv("SERVICE_NAME")
    resolved_region = aws_region or os.getenv("AWS_REGION", "us-east-1")

    reader = CloudWatchLogReader(region_name=resolved_region)

    return reader.read_recent_events(
        log_group_name=resolved_log_group,
        minutes=resolved_minutes,
        filter_pattern=resolved_filter_pattern,
        limit=resolved_limit,
        service_name=resolved_service_name,
    )


def load_events(
    source: Optional[str] = None,
    log_group_name: Optional[str] = None,
    minutes: Optional[int] = None,
    limit: Optional[int] = None,
    filter_pattern: Optional[str] = None,
    service_name: Optional[str] = None,
    aws_region: Optional[str] = None,
) -> List[LogEvent]:
    resolved_source = source or ("cloudwatch" if os.getenv("USE_CLOUDWATCH", "false").lower() == "true" else "sample")

    if resolved_source == "cloudwatch":
        print("[Worker] Source: CloudWatch Logs")
        return load_cloudwatch_logs(
            log_group_name=log_group_name,
            minutes=minutes,
            limit=limit,
            filter_pattern=filter_pattern,
            service_name=service_name,
            aws_region=aws_region,
        )

    print("[Worker] Source: sample logs")
    return load_sample_logs()


def run_pipeline(
    source: Optional[str] = None,
    use_llm: Optional[bool] = None,
    log_group_name: Optional[str] = None,
    minutes: Optional[int] = None,
    limit: Optional[int] = None,
    filter_pattern: Optional[str] = None,
    service_name: Optional[str] = None,
    aws_region: Optional[str] = None,
):
    print("[Worker] Loading logs...")
    events = load_events(
        source=source,
        log_group_name=log_group_name,
        minutes=minutes,
        limit=limit,
        filter_pattern=filter_pattern,
        service_name=service_name,
        aws_region=aws_region,
    )

    print(f"[Worker] Loaded {len(events)} events")

    analyzer = LogAnalyzer()
    result = analyzer.analyze(events)

    resolved_use_llm = use_llm if use_llm is not None else os.getenv("USE_LLM", "false").lower() == "true"

    if resolved_use_llm:
        print("[Worker] Using LLM summarizer")
        summarizer = LLMSummarizer(fallback=Summarizer())
    else:
        print("[Worker] Using deterministic summarizer")
        summarizer = Summarizer()

    summary = summarizer.summarize(result)

    slack = SlackClient()
    slack.send(summary)

    return summary


def main():
    run_pipeline()


if __name__ == "__main__":
    main()
