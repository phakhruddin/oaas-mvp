from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from app.models.log_event import LogEvent


@dataclass
class AnalysisResult:
    total_events: int
    error_count: int
    warning_count: int
    service_counts: Dict[str, int]
    level_counts: Dict[str, int]
    top_patterns: Dict[str, int]
    affected_services: List[str] = field(default_factory=list)
    severity: str = "low"
    evidence: List[str] = field(default_factory=list)


class LogAnalyzer:
    """Deterministic log analyzer used before AI summarization."""

    def analyze(self, events: List[LogEvent]) -> AnalysisResult:
        total_events = len(events)
        service_counter = Counter(event.service for event in events)
        level_counter = Counter(event.level.lower() for event in events)
        pattern_counter = Counter(event.summary_key() for event in events)

        error_events = [event for event in events if event.is_error()]
        warning_events = [event for event in events if event.is_warning()]
        affected_services = sorted({event.service for event in error_events})
        severity = self._calculate_severity(total_events, len(error_events), len(warning_events))
        evidence = self._build_evidence(error_events, warning_events, pattern_counter)

        return AnalysisResult(
            total_events=total_events,
            error_count=len(error_events),
            warning_count=len(warning_events),
            service_counts=dict(service_counter),
            level_counts=dict(level_counter),
            top_patterns=dict(pattern_counter.most_common(5)),
            affected_services=affected_services,
            severity=severity,
            evidence=evidence,
        )

    def _calculate_severity(self, total_events: int, error_count: int, warning_count: int) -> str:
        if total_events == 0:
            return "none"

        error_ratio = error_count / total_events

        if error_count >= 10 or error_ratio >= 0.50:
            return "critical"
        if error_count >= 3 or error_ratio >= 0.20:
            return "high"
        if error_count > 0 or warning_count >= 3:
            return "medium"
        return "low"

    def _build_evidence(
        self,
        error_events: List[LogEvent],
        warning_events: List[LogEvent],
        pattern_counter: Counter,
    ) -> List[str]:
        evidence: List[str] = []

        if error_events:
            first_error = error_events[0]
            evidence.append(
                f"First error from {first_error.service}: {first_error.message}"
            )

        if warning_events:
            evidence.append(f"Warnings detected: {len(warning_events)}")

        for pattern, count in pattern_counter.most_common(3):
            evidence.append(f"Pattern repeated {count} time(s): {pattern}")

        return evidence
