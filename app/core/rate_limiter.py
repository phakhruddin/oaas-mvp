import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RateLimitExceeded(Exception):
    pass


class TenantRateLimiter:
    """Simple in-memory sliding-window rate limiter per tenant."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, tenant_id: str) -> bool:
        now = time.time()
        requests = self._requests[tenant_id]

        while requests and now - requests[0] > self.window_seconds:
            requests.popleft()

        if len(requests) >= self.max_requests:
            return False

        requests.append(now)
        return True

    def enforce(self, tenant_id: str) -> None:
        if not self.allow(tenant_id):
            raise RateLimitExceeded(
                f"Tenant {tenant_id} exceeded rate limit: "
                f"{self.max_requests} requests / {self.window_seconds}s"
            )
