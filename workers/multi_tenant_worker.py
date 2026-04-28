import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.tenant_loader import TenantLoader
from app.services.analyzer import LogAnalyzer
from app.services.summarizer import Summarizer
from app.services.llm_summarizer import LLMSummarizer
from integrations.aws.cloudwatch import CloudWatchLogReader
from integrations.slack.slack_client import SlackClient


def process_tenant(tenant):
    print(f"\n[MultiTenant] Processing tenant: {tenant.display_name}")

    all_events = []

    for source in tenant.log_sources:
        print(f"[MultiTenant] Reading source: {source.name} ({source.log_group})")

        if source.provider != "cloudwatch":
            print(f"[MultiTenant] Skipping unsupported provider: {source.provider}")
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
        print(f"[MultiTenant] No events for tenant: {tenant.display_name}")
        return tenant.tenant_id, 0

    analyzer = LogAnalyzer()
    result = analyzer.analyze(all_events)

    if tenant.use_llm:
        summarizer = LLMSummarizer(fallback=Summarizer())
    else:
        summarizer = Summarizer()

    summary = summarizer.summarize(result)

    slack = SlackClient(webhook_url=tenant.slack_webhook_url)
    slack.send(summary)

    return tenant.tenant_id, len(all_events)


def main():
    config_path = os.getenv("TENANT_CONFIG_PATH", "config/tenants.json")
    max_workers = int(os.getenv("TENANT_WORKER_THREADS", "4"))

    loader = TenantLoader(config_path=config_path)
    tenants = loader.load()

    print(f"[MultiTenant] Loaded {len(tenants)} tenants")
    print(f"[MultiTenant] Using {max_workers} worker threads")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_tenant, tenant): tenant for tenant in tenants}

        for future in as_completed(futures):
            tenant = futures[future]
            try:
                tenant_id, event_count = future.result()
                print(f"[MultiTenant] Completed tenant={tenant_id}, events={event_count}")
            except Exception as exc:
                print(f"[MultiTenant] Tenant failed: {tenant.display_name} ({tenant.tenant_id}) - {exc}")


if __name__ == "__main__":
    main()
