"""
Core MedMinder workflow logic.

This file makes the main safety-first workflow importable outside the notebook.
"""

from dataclasses import dataclass
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


def run_checkin_workflow(user_text: str, medicine_name: str, day: str, detected_text: str, user_confirmed: bool) -> Dict:
    safety = safety_screen(user_text)

    if not safety["allowed"]:
        return {
            "final_status": "blocked_and_escalated",
            "safety": safety,
            "reason": safety["reason"]
        }

    schedule = schedule_lookup(medicine_name, day)

    if schedule["status"] != "found":
        return {
            "final_status": "escalated",
            "safety": safety,
            "reason": "Medicine not found in active schedule."
        }

    med = schedule["medicine"]

    package = verify_package_text(
        expected_name=med["name"],
        expected_dosage=med["dosage"],
        detected_text=detected_text
    )

    if not package["package_match"]:
        return {
            "final_status": "escalated",
            "safety": safety,
            "schedule": schedule,
            "package": package,
            "reason": package["reason"]
        }

    if not user_confirmed:
        return {
            "final_status": "incomplete_and_escalated",
            "safety": safety,
            "schedule": schedule,
            "package": package,
            "reason": "User did not confirm completion."
        }

    return {
        "final_status": "completed",
        "safety": safety,
        "schedule": schedule,
        "package": package,
        "reason": "Check-in completed after schedule lookup, package match, and user confirmation."
    }


if __name__ == "__main__":
    demo = run_checkin_workflow(
        user_text="I am checking my scheduled medicine.",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="Rx: Amlodipine 5mg tablets. Take after breakfast.",
        user_confirmed=True
    )

    print(demo)
