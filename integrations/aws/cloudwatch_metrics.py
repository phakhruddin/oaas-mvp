import os
from typing import Dict, Optional


class CloudWatchMetricsClient:
    """Emit CloudWatch custom metrics with local fallback."""

    def __init__(self, namespace: Optional[str] = None, region_name: Optional[str] = None):
        self.namespace = namespace or os.getenv("METRICS_NAMESPACE", "OAAS/MVP")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.enabled = os.getenv("ENABLE_CLOUDWATCH_METRICS", "false").lower() == "true"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("boto3 required for CloudWatch metrics integration") from exc

            self._client = boto3.client("cloudwatch", region_name=self.region_name)

        return self._client

    def put_metric(
        self,
        name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        if not self.enabled:
            print(f"[Metrics] {name}={value} {unit} dimensions={dimensions or {}}")
            return

        metric_data = {
            "MetricName": name,
            "Value": value,
            "Unit": unit,
        }

        if dimensions:
            metric_data["Dimensions"] = [
                {"Name": key, "Value": value}
                for key, value in dimensions.items()
            ]

        self.client.put_metric_data(
            Namespace=self.namespace,
            MetricData=[metric_data],
        )
