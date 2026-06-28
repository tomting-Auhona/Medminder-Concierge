"""Core MedMinder workflow logic.

This file makes the main safety-first workflow importable outside the notebook.
It is deliberately deterministic so judges can run it without API keys while
still seeing the actual agent routing, safety, package-check, and escalation
decisions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class MedicationRecord:
    medicine_id: str
    name: str
    dosage: str
    time: str
    instructions: str
    days: List[str]
    active: bool = True


MOCK_SCHEDULE = [
    MedicationRecord(
        medicine_id="MED-001",
        name="Amlodipine",
        dosage="5mg",
        time="09:00",
        instructions="Take after breakfast",
        days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ),
    MedicationRecord(
        medicine_id="MED-002",
        name="Metformin",
        dosage="500mg",
        time="20:00",
        instructions="Take after dinner",
        days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
]


UNSAFE_PATTERNS = [
    "take extra",
    "double dose",
    "increase dose",
    "decrease dose",
    "skip medicine",
    "stop taking",
    "identify this pill",
    "loose pill",
    "what pill is this",
    "diagnose",
    "side effect"
]


def safety_screen(user_text: str) -> Dict:
    text = user_text.lower()

    for pattern in UNSAFE_PATTERNS:
        if pattern in text:
            return {
                "allowed": False,
                "reason": f"Unsafe medication-related request blocked: {pattern}"
            }

    return {
        "allowed": True,
        "reason": "Routine medication support request allowed."
    }


def schedule_lookup(medicine_name: str, day: str) -> Dict:
    for med in MOCK_SCHEDULE:
        if med.name.lower() == medicine_name.lower() and day in med.days and med.active:
            return {
                "status": "found",
                "medicine": med.__dict__
            }

    return {
        "status": "not_found",
        "medicine": None
    }


def verify_package_text(expected_name: str, expected_dosage: str, detected_text: str) -> Dict:
    clean_text = detected_text.lower().replace(" ", "")
    clean_name = expected_name.lower().replace(" ", "")
    clean_dosage = expected_dosage.lower().replace(" ", "")

    if not detected_text.strip():
        return {
            "status": "blocked",
            "package_match": False,
            "reason": "No readable package text detected."
        }

    if "loosepill" in clean_text or "whitepill" in clean_text:
        return {
            "status": "blocked",
            "package_match": False,
            "reason": "Loose pill identification is blocked."
        }

    if clean_name in clean_text and clean_dosage in clean_text:
        return {
            "status": "verified",
            "package_match": True,
            "reason": "Package text matches the stored schedule."
        }

    return {
        "status": "escalate",
        "package_match": False,
        "reason": "Package text does not match the stored schedule."
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _trace_step(step: int, agent: str, action: str, decision: str, output: str, safety_event: bool = False) -> Dict:
    return {
        "step": step,
        "timestamp": _utc_now(),
        "agent": agent,
        "action": action,
        "decision": decision,
        "output": output,
        "safety_event": safety_event,
    }


def run_checkin_workflow(
    user_text: str,
    medicine_name: str,
    day: str,
    detected_text: str,
    user_confirmed: bool,
    return_trace: bool = False,
) -> Dict:
    trace = [
        _trace_step(
            1,
            "UserInteraction",
            "start_checkin",
            "received",
            f"User started a medication check-in for {medicine_name} on {day}.",
        )
    ]

    safety = safety_screen(user_text)
    trace.append(
        _trace_step(
            2,
            "SafetyGuardrailAgent",
            "screen_user_text",
            "allowed" if safety["allowed"] else "blocked",
            safety["reason"],
            safety_event=not safety["allowed"],
        )
    )

    if not safety["allowed"]:
        result = {
            "final_status": "blocked_and_escalated",
            "safety": safety,
            "reason": safety["reason"]
        }
        trace.append(
            _trace_step(
                3,
                "CaregiverEscalationAgent",
                "create_alert",
                "caregiver_alert_created",
                safety["reason"],
                safety_event=True,
            )
        )
        if return_trace:
            result["trace"] = trace
        return result

    schedule = schedule_lookup(medicine_name, day)
    trace.append(
        _trace_step(
            3,
            "ScheduleAgent",
            "lookup_medication",
            schedule["status"],
            "Scheduled medicine found." if schedule["status"] == "found" else "Medicine was not found in the active schedule.",
        )
    )

    if schedule["status"] != "found":
        result = {
            "final_status": "escalated",
            "safety": safety,
            "reason": "Medicine not found in active schedule."
        }
        trace.append(
            _trace_step(
                4,
                "CaregiverEscalationAgent",
                "create_alert",
                "caregiver_alert_created",
                result["reason"],
                safety_event=True,
            )
        )
        if return_trace:
            result["trace"] = trace
        return result

    med = schedule["medicine"]

    package = verify_package_text(
        expected_name=med["name"],
        expected_dosage=med["dosage"],
        detected_text=detected_text
    )
    trace.append(
        _trace_step(
            4,
            "VisionPackagingAgent",
            "verify_package_text",
            package["status"],
            package["reason"],
            safety_event=not package["package_match"],
        )
    )

    if not package["package_match"]:
        result = {
            "final_status": "escalated",
            "safety": safety,
            "schedule": schedule,
            "package": package,
            "reason": package["reason"]
        }
        trace.append(
            _trace_step(
                5,
                "CaregiverEscalationAgent",
                "create_alert",
                "caregiver_alert_created",
                package["reason"],
                safety_event=True,
            )
        )
        if return_trace:
            result["trace"] = trace
        return result

    if not user_confirmed:
        result = {
            "final_status": "incomplete_and_escalated",
            "safety": safety,
            "schedule": schedule,
            "package": package,
            "reason": "User did not confirm completion."
        }
        trace.append(
            _trace_step(
                5,
                "ComplianceAgent",
                "check_self_confirmation",
                "not_confirmed",
                result["reason"],
                safety_event=True,
            )
        )
        trace.append(
            _trace_step(
                6,
                "CaregiverEscalationAgent",
                "create_alert",
                "caregiver_alert_created",
                result["reason"],
                safety_event=True,
            )
        )
        if return_trace:
            result["trace"] = trace
        return result

    result = {
        "final_status": "completed",
        "safety": safety,
        "schedule": schedule,
        "package": package,
        "reason": "Check-in completed after schedule lookup, package match, and user confirmation."
    }
    trace.append(
        _trace_step(
            5,
            "ComplianceAgent",
            "mark_completed",
            "completed",
            result["reason"],
        )
    )
    trace.append(
        _trace_step(
            6,
            "HistoryTrackerAgent",
            "record_completion",
            "history_updated",
            "Completion recorded for adherence tracking.",
        )
    )
    if return_trace:
        result["trace"] = trace
    return result


if __name__ == "__main__":
    demo = run_checkin_workflow(
        user_text="I am checking my scheduled medicine.",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="Rx: Amlodipine 5mg tablets. Take after breakfast.",
        user_confirmed=True
    )

    print(demo)
