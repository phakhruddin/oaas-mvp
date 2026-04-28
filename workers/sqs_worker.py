from integrations.aws.sqs_client import SQSClient
from app.models.job import AnalysisJob
from app.core.tenant_loader import TenantLoader
from workers.multi_tenant_worker import process_tenant


def main():
    sqs = SQSClient()
    loader = TenantLoader()

    print("[SQSWorker] Starting worker loop...")

    while True:
        messages = sqs.receive_messages(visibility_timeout=60)

        if not messages:
            continue

        tenants = loader.load()

        for msg in messages:
            try:
                job = AnalysisJob.from_dict(msg["body"])

                tenant = next(
                    t for t in tenants if t.tenant_id == job.tenant_id
                )

                print(f"[SQSWorker] Processing job for tenant={tenant.tenant_id}")
                process_tenant(tenant)

                sqs.delete_message(msg["receipt"])
                print(f"[SQSWorker] Completed job for tenant={tenant.tenant_id}")

            except Exception as exc:
                print(f"[SQSWorker] Job failed: {exc}")
                sqs.send_to_dlq(msg["body"], str(exc))
                sqs.delete_message(msg["receipt"])


if __name__ == "__main__":
    main()
