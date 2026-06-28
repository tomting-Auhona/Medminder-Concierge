import re
from datetime import datetime
from .config import ALLOWED_TOOLS, UNSAFE_MEDICATION_INTENTS


class MedMinderSecurityPolicy:
    def __init__(self):
        self.audit_log = []

    def redact_sensitive_text(self, text):
        if not isinstance(text, str):
            return text

        text = re.sub(r"\b(?:\+?\d[\d\s\-]{8,}\d)\b", "[REDACTED_PHONE]", text)
        text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", text)
        return text

    def is_safe_user_text(self, text):
        clean = (text or "").lower()

        for pattern in UNSAFE_MEDICATION_INTENTS:
            if pattern in clean:
                return False, "Blocked unsafe medication request: " + pattern

        return True, "Safe routine-support request."

    def validate_tool_name(self, tool_name):
        if tool_name not in ALLOWED_TOOLS:
            return False, "Tool is not allowlisted."

        return True, "Tool allowed."

    def safe_response(self, status, message, data=None):
        return {
            "status": status,
            "message": self.redact_sensitive_text(message),
            "data": data or {}
        }


security_policy = MedMinderSecurityPolicy()
