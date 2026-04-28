import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    environment: str
    aws_region: str
    cloudwatch_log_group: Optional[str]
    cloudwatch_limit: int
    cloudwatch_lookback_minutes: int
    cloudwatch_filter_pattern: str
    digest_lookback_minutes: int
    service_name: Optional[str]
    use_llm: bool
    openai_model: str
    slack_webhook_url: Optional[str]


def load_env_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


def load_config(environment: Optional[str] = None) -> AppConfig:
    resolved_env = environment or os.getenv("OAAS_ENV", "dev")

    # load environment configs
    load_env_file(f"config/{resolved_env}.env")
    load_env_file("config/local.env")

    return AppConfig(
        environment=resolved_env,
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        cloudwatch_log_group=os.getenv("CLOUDWATCH_LOG_GROUP"),
        cloudwatch_limit=int(os.getenv("CLOUDWATCH_LIMIT", "100")),
        cloudwatch_lookback_minutes=int(os.getenv("CLOUDWATCH_LOOKBACK_MINUTES", "15")),
        cloudwatch_filter_pattern=os.getenv("CLOUDWATCH_FILTER_PATTERN", ""),
        digest_lookback_minutes=int(os.getenv("DIGEST_LOOKBACK_MINUTES", "1440")),
        service_name=os.getenv("SERVICE_NAME"),
        use_llm=os.getenv("USE_LLM", "false").lower() == "true",
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
    )