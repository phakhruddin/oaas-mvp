import json
import os
from typing import List


class SQSClient:
    """Lightweight SQS client with local fallback."""

    def __init__(self, queue_url: str | None = None):
        self.queue_url = queue_url or os.getenv("SQS_QUEUE_URL")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError:
                raise RuntimeError("boto3 required for SQS integration")

            self._client = boto3.client("sqs")
        return self._client

    def send_message(self, message: dict):
        if not self.queue_url:
            print("[SQS] No queue configured. Local fallback:", message)
            return

        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
        )

    def receive_messages(self, max_messages: int = 5) -> List[dict]:
        if not self.queue_url:
            return []

        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])

        results = []
        for msg in messages:
            results.append({
                "body": json.loads(msg["Body"]),
                "receipt": msg["ReceiptHandle"],
            })

        return results

    def delete_message(self, receipt_handle: str):
        if not self.queue_url:
            return

        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
