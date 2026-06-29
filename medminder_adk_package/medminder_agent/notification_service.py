"""Caregiver notification helpers for MedMinder.

The default implementation uses ntfy.sh because it works from a phone app
without account setup. It is still demo-safe: no real patient data is required.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict
from urllib import request
from urllib.error import URLError


DEFAULT_TOPIC = "medminder-concierge-demo"


def build_caregiver_alert(result: Dict, topic: str = DEFAULT_TOPIC) -> Dict:
    status = result.get("final_status", "unknown")
    reason = result.get("reason", "No reason provided.")

    return {
        "topic": topic,
        "title": f"MedMinder alert: {status}",
        "message": reason,
        "priority": "urgent" if "blocked" in status or "escalated" in status else "default",
        "tags": ["warning", "pill"] if status != "completed" else ["white_check_mark"],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def send_ntfy_alert(alert: Dict, dry_run: bool = False) -> Dict:
    """Send an alert to ntfy.sh or return the payload in dry-run mode."""
    topic = alert.get("topic") or os.getenv("MEDMINDER_NTFY_TOPIC") or DEFAULT_TOPIC
    payload = alert["message"].encode("utf-8")
    url = f"https://ntfy.sh/{topic}"

    headers = {
        "Title": alert["title"],
        "Priority": "5" if alert.get("priority") == "urgent" else "3",
        "Tags": ",".join(alert.get("tags", [])),
    }

    if dry_run:
        return {
            "sent": False,
            "dry_run": True,
            "provider": "ntfy",
            "url": url,
            "headers": headers,
            "message": alert["message"],
        }

    req = request.Request(url=url, data=payload, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "sent": True,
                "dry_run": False,
                "provider": "ntfy",
                "status_code": response.status,
                "response": json.loads(body) if body else {},
                "url": url,
            }
    except (OSError, URLError) as exc:
        return {
            "sent": False,
            "dry_run": False,
            "provider": "ntfy",
            "error": str(exc),
            "url": url,
        }
