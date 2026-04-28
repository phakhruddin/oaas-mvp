import random
import time
from typing import Callable, Iterable, Optional, TypeVar

T = TypeVar("T")


class RetryConfig:
    def __init__(
        self,
        attempts: int = 3,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 10.0,
        jitter_seconds: float = 0.25,
        retryable_exceptions: Optional[Iterable[type[BaseException]]] = None,
    ):
        self.attempts = attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.jitter_seconds = jitter_seconds
        self.retryable_exceptions = tuple(retryable_exceptions or [Exception])


def with_retry(operation: Callable[[], T], config: Optional[RetryConfig] = None) -> T:
    """Run an operation with exponential backoff and jitter."""
    resolved_config = config or RetryConfig()
    last_exception: Optional[BaseException] = None

    for attempt in range(1, resolved_config.attempts + 1):
        try:
            return operation()
        except resolved_config.retryable_exceptions as exc:
            last_exception = exc

            if attempt == resolved_config.attempts:
                break

            delay = min(
                resolved_config.base_delay_seconds * (2 ** (attempt - 1)),
                resolved_config.max_delay_seconds,
            )
            delay += random.uniform(0, resolved_config.jitter_seconds)

            print(
                f"[Retry] Attempt {attempt} failed: {exc}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)

    raise last_exception  # type: ignore[misc]
