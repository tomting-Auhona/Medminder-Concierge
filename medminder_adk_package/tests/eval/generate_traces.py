import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from medminder_agent.core_workflow import run_checkin_workflow

DATASET = ROOT / "tests" / "eval" / "datasets" / "medminder-eval-dataset.json"
TRACE = ROOT / "artifacts" / "traces" / "generated_traces.json"
SUMMARY = ROOT / "artifacts" / "traces" / "eval_summary.md"


def has_caregiver_alert(trace):
    return any(step["agent"] == "CaregiverEscalationAgent" for step in trace)


def has_safety_event(trace):
    return any(step["safety_event"] for step in trace)


def evaluate(case):
    user_input = case["input"]
    result = run_checkin_workflow(
        user_text=user_input["user_text"],
        medicine_name=user_input["medicine_name"],
        day=user_input["day"],
        detected_text=user_input["package_text"],
        user_confirmed=user_input["user_confirmed"],
        return_trace=True,
    )

    actual = {
        "final_status": result["final_status"],
        "caregiver_alert": has_caregiver_alert(result["trace"]),
        "safety_event": has_safety_event(result["trace"]),
    }

    return {
        "case_id": case["id"],
        "description": case["description"],
        "input": user_input,
        "expected": case["expected"],
        "actual": actual,
        "passed": actual == case["expected"],
        "reason": result["reason"],
        "trace": result["trace"],
    }


def write_summary(traces):
    lines = [
        "# MedMinder Deterministic Evaluation Summary",
        "",
        "| Case | Expected Status | Actual Status | Caregiver Alert | Safety Event | Passed |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for item in traces:
        lines.append(
            "| {case_id} | {expected} | {actual} | {alert} | {event} | {passed} |".format(
                case_id=item["case_id"],
                expected=item["expected"]["final_status"],
                actual=item["actual"]["final_status"],
                alert=item["actual"]["caregiver_alert"],
                event=item["actual"]["safety_event"],
                passed=item["passed"],
            )
        )

    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    traces = [evaluate(case) for case in cases]

    TRACE.parent.mkdir(parents=True, exist_ok=True)
    TRACE.write_text(json.dumps(traces, indent=2), encoding="utf-8")
    write_summary(traces)

    passed = sum(item["passed"] for item in traces)
    total = len(traces)

    print(f"Generated traces: {TRACE}")
    print(f"Generated summary: {SUMMARY}")
    print(f"Passed {passed}/{total} real workflow evaluation cases.")

    if passed != total:
        raise SystemExit("Some real workflow evaluation cases failed.")


if __name__ == "__main__":
    main()
