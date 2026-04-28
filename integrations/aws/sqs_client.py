import json
import os
from typing import List


class SQSClient:
    """Lightweight SQS client with local fallback and optional DLQ support."""

    def __init__(self, queue_url: str | None = None, dlq_url: str | None = None):
        self.queue_url = queue_url or os.getenv("SQS_QUEUE_URL")
        self.dlq_url = dlq_url or os.getenv("SQS_DLQ_URL")
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

    def send_to_dlq(self, message: dict, error: str):
        payload = {
            "failed_message": message,
            "error": error,
        }

        if not self.dlq_url:
            print("[SQS] No DLQ configured. Failed message:", payload)
            return

        self.client.send_message(
            QueueUrl=self.dlq_url,
            MessageBody=json.dumps(payload),
        )

    def receive_messages(self, max_messages: int = 5, visibility_timeout: int | None = None) -> List[dict]:
        if not self.queue_url:
            return []

        request = {
            "QueueUrl": self.queue_url,
            "MaxNumberOfMessages": max_messages,
            "WaitTimeSeconds": 10,
        }

        if visibility_timeout is not None:
            request["VisibilityTimeout"] = visibility_timeout

        response = self.client.receive_message(**request)

        messages = response.get("Messages", [])

        results = []
        for msg in messages:
            results.append({
                "body": json.loads(msg["Body"]),
                "receipt": msg["ReceiptHandle"],
                "message_id": msg.get("MessageId"),
            })

        return results

    def delete_message(self, receipt_handle: str):
        if not self.queue_url:
            return

        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
