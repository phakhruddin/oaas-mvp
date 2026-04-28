import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.logger import get_logger
from app.core.tenant_loader import TenantLoader
from app.services.analyzer import LogAnalyzer
from app.services.summarizer import Summarizer
from app.services.llm_summarizer import LLMSummarizer
from integrations.aws.cloudwatch import CloudWatchLogReader
from integrations.slack.slack_client import SlackClient

logger = get_logger("tenant_worker")


def process_tenant(tenant, trace_id=None):
    logger.info(
        "processing tenant",
        extra={"trace_id": trace_id, "tenant_id": tenant.tenant_id},
    )

    all_events = []

    for source in tenant.log_sources:
        logger.info(
            "reading source",
            extra={"trace_id": trace_id, "tenant_id": tenant.tenant_id, "source_name": source.name},
        )

        if source.provider != "cloudwatch":
            continue

        reader = CloudWatchLogReader(region_name=source.region)

        events = reader.read_recent_events(
            log_group_name=source.log_group,
            minutes=source.lookback_minutes,
            filter_pattern=source.filter_pattern,
            limit=source.limit,
            service_name=source.service_name,
        )

        all_events.extend(events)

    if not all_events:
        logger.info(
            "no events",
            extra={"trace_id": trace_id, "tenant_id": tenant.tenant_id},
        )
        return tenant.tenant_id, 0

    analyzer = LogAnalyzer()
    result = analyzer.analyze(all_events)

    if tenant.use_llm:
        summarizer = LLMSummarizer(fallback=Summarizer())
    else:
        summarizer = Summarizer()

    summary = summarizer.summarize(result)

    if trace_id:
        summary = f"[trace_id={trace_id}]\n\n{summary}"

    slack = SlackClient(webhook_url=tenant.slack_webhook_url)
    slack.send(summary)

    return tenant.tenant_id, len(all_events)


def main():
    config_path = os.getenv("TENANT_CONFIG_PATH", "config/tenants.json")
    max_workers = int(os.getenv("TENANT_WORKER_THREADS", "4"))

    loader = TenantLoader(config_path=config_path)
    tenants = loader.load()

    logger.info(f"loaded {len(tenants)} tenants")
    logger.info(f"using {max_workers} worker threads")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_tenant, tenant): tenant for tenant in tenants}

        for future in as_completed(futures):
            tenant = futures[future]
            try:
                tenant_id, event_count = future.result()
                logger.info(
                    "tenant completed",
                    extra={"tenant_id": tenant_id, "trace_id": None},
                )
            except Exception as exc:
                logger.error(
                    f"tenant failed: {exc}",
                    extra={"tenant_id": tenant.tenant_id},
                )


if __name__ == "__main__":
    main()
