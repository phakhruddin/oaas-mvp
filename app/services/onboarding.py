from dataclasses import dataclass
from typing import Dict

from app.core.api_keys import issue_api_key


@dataclass
class DemoTenant:
    tenant_id: str
    api_key: str
    sample_log_group: str


class OnboardingService:
    def create_demo_tenant(self, tenant_id: str) -> DemoTenant:
        issued = issue_api_key(tenant_id)

        return DemoTenant(
            tenant_id=tenant_id,
            api_key=issued.api_key,
            sample_log_group="/aws/lambda/demo-service",
        )

    def onboarding_response(self, tenant_id: str) -> Dict:
        demo = self.create_demo_tenant(tenant_id)

        return {
            "tenant_id": demo.tenant_id,
            "api_key": demo.api_key,
            "next_steps": [
                "Set API key in request header",
                "Connect CloudWatch log group",
                "Run analyze endpoint",
            ],
        }
