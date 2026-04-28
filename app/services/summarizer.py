from dataclasses import dataclass
from typing import List

from app.services.analyzer import AnalysisResult


@dataclass
class IncidentSummary:
    title: str
    severity: str
    summary: str
    evidence: List[str]
    next_steps: List[str]


class Summarizer:
    """Convert AnalysisResult into human-readable incident summary."""

    def summarize(self, result: AnalysisResult) -> IncidentSummary:
        title = self._build_title(result)
        summary = self._build_summary(result)
        next_steps = self._suggest_next_steps(result)

        return IncidentSummary(
            title=title,
            severity=result.severity,
            summary=summary,
            evidence=result.evidence,
            next_steps=next_steps,
        )

    def _build_title(self, result: AnalysisResult) -> str:
        if not result.affected_services:
            return "No significant incident detected"

        service = result.affected_services[0]
        return f"{service} service degraded"

    def _build_summary(self, result: AnalysisResult) -> str:
        return (
            f"Processed {result.total_events} logs. "
            f"Errors: {result.error_count}, Warnings: {result.warning_count}. "
            f"Affected services: {', '.join(result.affected_services) or 'none'}."
        )

    def _suggest_next_steps(self, result: AnalysisResult) -> List[str]:
        steps = []

        if result.error_count > 0:
            steps.append("Check recent deployments for affected services")
            steps.append("Inspect logs around first error occurrence")

        if result.severity in ["high", "critical"]:
            steps.append("Check infrastructure dependencies (DB, cache, network)")

        if not steps:
            steps.append("No action required")

        return steps
