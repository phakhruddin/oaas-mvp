import time
from typing import Dict


class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    """Simple per-tenant circuit breaker."""

    def __init__(self, failure_threshold: int = 3, recovery_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}

    def before_call(self, tenant_id: str):
        if tenant_id not in self.failures:
            return

        if self.failures[tenant_id] < self.failure_threshold:
            return

        last_failure = self.last_failure_time.get(tenant_id, 0)
        if time.time() - last_failure < self.recovery_seconds:
            raise CircuitOpen(f"Circuit open for tenant={tenant_id}")

        # Reset after cooldown
        self.failures[tenant_id] = 0

    def record_success(self, tenant_id: str):
        self.failures[tenant_id] = 0

    def record_failure(self, tenant_id: str):
        self.failures[tenant_id] = self.failures.get(tenant_id, 0) + 1
        self.last_failure_time[tenant_id] = time.time()
