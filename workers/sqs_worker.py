import time

from integrations.aws.sqs_client import SQSClient
from integrations.aws.cloudwatch_metrics import CloudWatchMetricsClient
from app.models.job import AnalysisJob
from app.core.tenant_loader import TenantLoader
from workers.multi_tenant_worker import process_tenant


def main():
    sqs = SQSClient()
    metrics = CloudWatchMetricsClient()
    loader = TenantLoader()

    print("[SQSWorker] Starting worker loop...")

    while True:
        messages = sqs.receive_messages(visibility_timeout=60)

        if not messages:
            continue

        tenants = loader.load()

        for msg in messages:
            start_time = time.time()

            try:
                job = AnalysisJob.from_dict(msg["body"])

                tenant = next(
                    t for t in tenants if t.tenant_id == job.tenant_id
                )

                print(f"[SQSWorker] Processing job for tenant={tenant.tenant_id}")

                process_tenant(tenant)

                duration = time.time() - start_time

                metrics.put_metric(
                    name="JobSuccess",
                    value=1,
                    dimensions={"tenant_id": tenant.tenant_id},
                )

                metrics.put_metric(
                    name="JobLatency",
                    value=duration,
                    unit="Seconds",
                    dimensions={"tenant_id": tenant.tenant_id},
                )

                sqs.delete_message(msg["receipt"])

                print(f"[SQSWorker] Completed job for tenant={tenant.tenant_id} in {duration:.2f}s")

            except Exception as exc:
                duration = time.time() - start_time

                print(f"[SQSWorker] Job failed: {exc}")

                metrics.put_metric(
                    name="JobFailure",
                    value=1,
                    dimensions={"tenant_id": job.tenant_id if 'job' in locals() else "unknown"},
                )

                metrics.put_metric(
                    name="JobLatency",
                    value=duration,
                    unit="Seconds",
                    dimensions={"tenant_id": job.tenant_id if 'job' in locals() else "unknown"},
                )

                sqs.send_to_dlq(msg["body"], str(exc))
                sqs.delete_message(msg["receipt"])


if __name__ == "__main__":
    main()
