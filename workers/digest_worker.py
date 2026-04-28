import os

from integrations.aws.cloudwatch import CloudWatchLogReader
from app.services.digest import DailyDigestService


def load_cloudwatch_events():
    log_group = os.getenv("CLOUDWATCH_LOG_GROUP")
    region = os.getenv("AWS_REGION", "us-east-1")
    minutes = int(os.getenv("DIGEST_LOOKBACK_MINUTES", "1440"))  # default 24h
    limit = int(os.getenv("CLOUDWATCH_LIMIT", "500"))

    if not log_group:
        raise ValueError("CLOUDWATCH_LOG_GROUP must be set for digest job")

    reader = CloudWatchLogReader(region_name=region)

    return reader.read_recent_events(
        log_group_name=log_group,
        minutes=minutes,
        limit=limit,
    )


def main():
    print("[DigestWorker] Loading events for digest...")
    events = load_cloudwatch_events()

    print(f"[DigestWorker] Loaded {len(events)} events")

    service = DailyDigestService()
    digest = service.build(events)

    output = service.format(digest)

    print("\n[DigestWorker] Daily Digest Output:\n")
    print(output)


if __name__ == "__main__":
    main()
