import argparse
import json
from pathlib import Path

from medminder_agent.core_workflow import run_checkin_workflow


SCENARIOS = {
    "success": {
        "user_text": "I am checking my scheduled medicine.",
        "medicine_name": "Amlodipine",
        "day": "Monday",
        "package_text": "Rx: Amlodipine 5mg tablets. Take after breakfast.",
        "user_confirmed": True,
    },
    "wrong-package": {
        "user_text": "I am checking my scheduled medicine.",
        "medicine_name": "Amlodipine",
        "day": "Monday",
        "package_text": "Rx: Metformin 500mg tablets. Take after dinner.",
        "user_confirmed": True,
    },
    "loose-pill": {
        "user_text": "I found this pill.",
        "medicine_name": "Amlodipine",
        "day": "Monday",
        "package_text": "Loose white pill on the table.",
        "user_confirmed": True,
    },
    "unsafe-dose": {
        "user_text": "Should I take extra medicine today?",
        "medicine_name": "Amlodipine",
        "day": "Monday",
        "package_text": "Rx: Amlodipine 5mg tablets. Take after breakfast.",
        "user_confirmed": True,
    },
    "no-confirmation": {
        "user_text": "I am checking my scheduled medicine.",
        "medicine_name": "Amlodipine",
        "day": "Monday",
        "package_text": "Rx: Amlodipine 5mg tablets. Take after breakfast.",
        "user_confirmed": False,
    },
}


def render_trace(result):
    print("\nMedMinder Concierge live workflow trace")
    print("=" * 48)

    for step in result["trace"]:
        marker = " SAFETY" if step["safety_event"] else ""
        print(
            f"{step['step']:02d}. [{step['agent']}] "
            f"{step['action']} -> {step['decision']}{marker}"
        )
        print(f"    {step['output']}")

    print("-" * 48)
    print(f"Final status: {result['final_status']}")
    print(f"Reason: {result['reason']}")


def main():
    parser = argparse.ArgumentParser(description="Run the MedMinder Concierge executable demo.")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        default="success",
        help="Demo scenario to execute.",
    )
    parser.add_argument(
        "--json-output",
        default="artifacts/demo/latest_demo_trace.json",
        help="Where to save the full JSON result.",
    )
    args = parser.parse_args()

    scenario = SCENARIOS[args.scenario]
    result = run_checkin_workflow(
        user_text=scenario["user_text"],
        medicine_name=scenario["medicine_name"],
        day=scenario["day"],
        detected_text=scenario["package_text"],
        user_confirmed=scenario["user_confirmed"],
        return_trace=True,
    )

    output = Path(args.json_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    render_trace(result)
    print(f"Saved JSON trace: {output}")


if __name__ == "__main__":
    main()
