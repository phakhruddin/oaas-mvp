import json
import os
from typing import Optional

from app.services.analyzer import AnalysisResult
from app.services.summarizer import IncidentSummary, Summarizer


class LLMSummarizer:
    """Optional LLM-backed summarizer.

    This layer receives compact analyzer output, not raw logs.
    If no API key is configured or the provider call fails, it falls back to
    the deterministic Summarizer.
    """

    def __init__(self, fallback: Optional[Summarizer] = None):
        self.fallback = fallback or Summarizer()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def summarize(self, result: AnalysisResult) -> IncidentSummary:
        if not self.api_key:
            print("[LLMSummarizer] OPENAI_API_KEY not set. Using deterministic fallback.")
            return self.fallback.summarize(result)

        try:
            return self._summarize_with_openai(result)
        except Exception as exc:
            print(f"[LLMSummarizer] LLM summarization failed: {exc}. Using fallback.")
            return self.fallback.summarize(result)

    def _summarize_with_openai(self, result: AnalysisResult) -> IncidentSummary:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is required. Install with: pip install openai") from exc

        client = OpenAI(api_key=self.api_key)
        prompt = self._build_prompt(result)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an SRE assistant. Summarize compact log analysis into "
                        "a cautious incident summary. Do not claim certainty. Return only JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)

        return IncidentSummary(
            title=payload.get("title", "Incident summary"),
            severity=payload.get("severity", result.severity),
            summary=payload.get("summary", self.fallback.summarize(result).summary),
            evidence=payload.get("evidence", result.evidence),
            next_steps=payload.get("next_steps", self.fallback.summarize(result).next_steps),
        )

    def _build_prompt(self, result: AnalysisResult) -> str:
        compact_analysis = {
            "total_events": result.total_events,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "service_counts": result.service_counts,
            "level_counts": result.level_counts,
            "top_patterns": result.top_patterns,
            "affected_services": result.affected_services,
            "severity": result.severity,
            "evidence": result.evidence,
        }

        return (
            "Create an incident summary from this compact log analysis. "
            "Return JSON with keys: title, severity, summary, evidence, next_steps.\n\n"
            f"Analysis:\n{json.dumps(compact_analysis, indent=2)}"
        )
