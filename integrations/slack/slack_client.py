import os
import json
import urllib.request

from app.services.summarizer import IncidentSummary


class SlackClient:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def send(self, summary: IncidentSummary):
        message = self._format_message(summary)

        if not self.webhook_url:
            print("[SlackClient] No webhook configured. Printing message:\n")
            print(message)
            return

        payload = {"text": message}

        req = urllib.request.Request(
            self.webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    print(f"Slack error: {response.status}")
        except Exception as e:
            print(f"Slack send failed: {e}")

    def _format_message(self, summary: IncidentSummary) -> str:
        lines = [
            f"🚨 {summary.title}",
            f"Severity: {summary.severity.upper()}",
            "",
            summary.summary,
            "",
            "Evidence:",
        ]

        lines.extend([f"- {e}" for e in summary.evidence])

        lines.append("")
        lines.append("Next steps:")
        lines.extend([f"- {step}" for step in summary.next_steps])

        return "\n".join(lines)
