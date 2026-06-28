import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from medminder_agent.core_workflow import run_checkin_workflow


def test_successful_checkin():
    result = run_checkin_workflow(
        user_text="I am checking my scheduled medicine.",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="Rx: Amlodipine 5mg tablets. Take after breakfast.",
        user_confirmed=True,
        return_trace=True,
    )

    assert result["final_status"] == "completed"
    assert [step["agent"] for step in result["trace"]] == [
        "UserInteraction",
        "SafetyGuardrailAgent",
        "ScheduleAgent",
        "VisionPackagingAgent",
        "ComplianceAgent",
        "HistoryTrackerAgent",
    ]


def test_wrong_package_escalates():
    result = run_checkin_workflow(
        user_text="I am checking my scheduled medicine.",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="Rx: Metformin 500mg tablets. Take after dinner.",
        user_confirmed=True,
        return_trace=True,
    )

    assert result["final_status"] == "escalated"
    assert result["trace"][-1]["agent"] == "CaregiverEscalationAgent"


def test_unsafe_dosage_request_blocks():
    result = run_checkin_workflow(
        user_text="Should I take extra medicine?",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="Rx: Amlodipine 5mg tablets. Take after breakfast.",
        user_confirmed=True,
        return_trace=True,
    )

    assert result["final_status"] == "blocked_and_escalated"
    assert result["trace"][-1]["agent"] == "CaregiverEscalationAgent"


def test_missing_package_text_escalates():
    result = run_checkin_workflow(
        user_text="I am checking my scheduled medicine.",
        medicine_name="Amlodipine",
        day="Monday",
        detected_text="",
        user_confirmed=True,
        return_trace=True,
    )

    assert result["final_status"] == "escalated"
    assert result["trace"][-1]["agent"] == "CaregiverEscalationAgent"
