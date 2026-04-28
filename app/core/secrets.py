import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional


class SecretsManager:
    """Resolve secrets from AWS Secrets Manager with environment fallback.

    Local development can keep using environment variables. In AWS, set
    ENABLE_AWS_SECRETS=true and provide secret names through env vars.
    """

    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.enabled = os.getenv("ENABLE_AWS_SECRETS", "false").lower() == "true"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("boto3 is required for AWS Secrets Manager integration") from exc

            self._client = boto3.client("secretsmanager", region_name=self.region_name)

        return self._client

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        response = self.client.get_secret_value(SecretId=secret_name)
        raw_secret = response.get("SecretString", "{}")

        try:
            return json.loads(raw_secret)
        except json.JSONDecodeError:
            return {"value": raw_secret}

    def get_value(self, env_name: str, secret_name_env: Optional[str] = None, key: Optional[str] = None) -> Optional[str]:
        env_value = os.getenv(env_name)
        if env_value:
            return env_value

        if not self.enabled or not secret_name_env:
            return None

        secret_name = os.getenv(secret_name_env)
        if not secret_name:
            return None

        payload = self.get_secret(secret_name)
        lookup_key = key or env_name

        value = payload.get(lookup_key)
        return str(value) if value is not None else None
