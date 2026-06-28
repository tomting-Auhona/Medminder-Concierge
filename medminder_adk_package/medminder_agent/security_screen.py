import re
from dataclasses import dataclass, field
from typing import Dict, List
from .config import PROMPT_INJECTION_PATTERNS, UNSAFE_MEDICATION_INTENTS


@dataclass
class SecurityScreenResult:
    allowed: bool
    sanitized_text: str
    security_events: List[str] = field(default_factory=list)
    redactions: Dict[str, int] = field(default_factory=dict)
    route: str = "continue"


class MedMinderSecurityScreen:
    def redact_pii(self, text):
        redactions = {"phone_numbers": 0, "emails": 0}

        def phone_repl(match):
            redactions["phone_numbers"] += 1
            return "[REDACTED_PHONE]"

        def email_repl(match):
            redactions["emails"] += 1
            return "[REDACTED_EMAIL]"

        text = re.sub(r"\b(?:\+?\d[\d\s\-]{8,}\d)\b", phone_repl, text or "")
        text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email_repl, text)

        return text, redactions

    def screen(self, user_text):
        sanitized, redactions = self.redact_pii(user_text or "")
        lower = sanitized.lower()

        events = []

        if sum(redactions.values()) > 0:
            events.append("pii_redacted")

        if any(pattern in lower for pattern in PROMPT_INJECTION_PATTERNS):
            events.append("prompt_injection_detected")

        if any(pattern in lower for pattern in UNSAFE_MEDICATION_INTENTS):
            events.append("unsafe_medication_intent_detected")

        allowed = (
            "prompt_injection_detected" not in events
            and "unsafe_medication_intent_detected" not in events
        )

        return SecurityScreenResult(
            allowed=allowed,
            sanitized_text=sanitized,
            security_events=events,
            redactions=redactions,
            route="continue" if allowed else "escalate_to_caregiver",
        )


security_screen = MedMinderSecurityScreen()
