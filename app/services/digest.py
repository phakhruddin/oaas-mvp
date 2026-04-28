from dataclasses import dataclass
from typing import Dict, List

from app.models.log_event import LogEvent
from app.services.analyzer import LogAnalyzer


@dataclass
class DailyDigest:
    title: str
    total_events: int
    error_count: int
    warning_count: int
    noisiest_service: str
    affected_services: List[str]
    top_patterns: Dict[str, int]
    recommendations: List[str]


class DailyDigestService:
    """Create a daily operational digest from normalized log events."""

    def __init__(self):
        self.analyzer = LogAnalyzer()

    def build(self, events: List[LogEvent]) -> DailyDigest:
        result = self.analyzer.analyze(events)
        noisiest_service = self._find_noisiest_service(result.service_counts)

        return DailyDigest(
            title="Daily Observability Digest",
            total_events=result.total_events,
            error_count=result.error_count,
            warning_count=result.warning_count,
            noisiest_service=noisiest_service,
            affected_services=result.affected_services,
            top_patterns=result.top_patterns,
            recommendations=self._recommend(result.error_count, result.warning_count),
        )

    def format(self, digest: DailyDigest) -> str:
        lines = [
            f"📊 {digest.title}",
            "",
            f"Total events: {digest.total_events}",
            f"Errors: {digest.error_count}",
            f"Warnings: {digest.warning_count}",
            f"Noisiest service: {digest.noisiest_service}",
            f"Affected services: {', '.join(digest.affected_services) or 'none'}",
            "",
            "Top patterns:",
        ]

        if digest.top_patterns:
            lines.extend([f"- {pattern}: {count}" for pattern, count in digest.top_patterns.items()])
        else:
            lines.append("- none")

        lines.append("")
        lines.append("Recommendations:")
        lines.extend([f"- {item}" for item in digest.recommendations])

        return "\n".join(lines)

    def _find_noisiest_service(self, service_counts: Dict[str, int]) -> str:
        if not service_counts:
            return "none"

        return max(service_counts, key=service_counts.get)

    def _recommend(self, error_count: int, warning_count: int) -> List[str]:
        recommendations: List[str] = []

        if error_count > 0:
            recommendations.append("Review error patterns and recent deployments for affected services")

        if warning_count > 5:
            recommendations.append("Review warning noise and decide whether alerts should be tuned")

        if not recommendations:
            recommendations.append("No immediate action required")

        return recommendations
