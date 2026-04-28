import time

from app.core.logger import get_logger
from app.core.tenant_loader import TenantLoader
from app.models.job import AnalysisJob
from integrations.aws.cloudwatch_metrics import CloudWatchMetricsClient
from integrations.aws.sqs_client import SQSClient
from workers.multi_tenant_worker import process_tenant

logger = get_logger("sqs_worker")


def main():
    sqs = SQSClient()
    metrics = CloudWatchMetricsClient()
    loader = TenantLoader()

    logger.info("starting worker loop")

    while True:
        messages = sqs.receive_messages(visibility_timeout=60)

        if not messages:
            continue

        tenants = loader.load()

        for msg in messages:
            start_time = time.time()
            job = None
            trace_id = "unknown"
            tenant_id = "unknown"

            try:
                job = AnalysisJob.from_dict(msg["body"])
                trace_id = (job.metadata or {}).get("trace_id", "unknown")
                tenant_id = job.tenant_id

                tenant = next(t for t in tenants if t.tenant_id == job.tenant_id)

                logger.info(
                    "processing job",
                    extra={"trace_id": trace_id, "tenant_id": tenant.tenant_id, "job_type": job.job_type},
                )

                process_tenant(tenant, trace_id=trace_id)

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

                logger.info(
                    f"completed job in {duration:.2f}s",
                    extra={"trace_id": trace_id, "tenant_id": tenant.tenant_id, "job_type": job.job_type},
                )

            except Exception as exc:
                duration = time.time() - start_time

                logger.error(
                    f"job failed: {exc}",
                    extra={"trace_id": trace_id, "tenant_id": tenant_id},
                )

                metrics.put_metric(
                    name="JobFailure",
                    value=1,
                    dimensions={"tenant_id": tenant_id},
                )

                metrics.put_metric(
                    name="JobLatency",
                    value=duration,
                    unit="Seconds",
                    dimensions={"tenant_id": tenant_id},
                )

                sqs.send_to_dlq(msg["body"], str(exc))
                sqs.delete_message(msg["receipt"])


if __name__ == "__main__":
    main()
