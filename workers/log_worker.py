from datetime import datetime

from app.models.log_event import LogEvent
from app.services.analyzer import LogAnalyzer
from app.services.summarizer import Summarizer
from integrations.slack.slack_client import SlackClient


def load_sample_logs():
    return [
        LogEvent(datetime.utcnow(), "payment-service", "error", "DB timeout"),
        LogEvent(datetime.utcnow(), "payment-service", "error", "DB timeout"),
        LogEvent(datetime.utcnow(), "payment-service", "warn", "Retrying connection"),
        LogEvent(datetime.utcnow(), "checkout-service", "info", "Request received"),
        LogEvent(datetime.utcnow(), "checkout-service", "error", "Null pointer exception"),
    ]


def main():
    print("[Worker] Loading logs...")
    events = load_sample_logs()

    print(f"[Worker] Loaded {len(events)} events")

    analyzer = LogAnalyzer()
    result = analyzer.analyze(events)

    summarizer = Summarizer()
    summary = summarizer.summarize(result)

    slack = SlackClient()
    slack.send(summary)


if __name__ == "__main__":
    main()
