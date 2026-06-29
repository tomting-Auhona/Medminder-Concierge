import argparse
import json
from pathlib import Path

from medminder_agent.core_workflow import run_checkin_workflow
from medminder_agent.notification_service import build_caregiver_alert, send_ntfy_alert


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
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Send a real caregiver alert through ntfy.sh when escalation happens.",
    )
    parser.add_argument(
        "--ntfy-topic",
        default="medminder-concierge-demo",
        help="ntfy.sh topic to publish caregiver alerts to.",
    )
    args = parser.parse_args()

    scenario = SCENARIOS[args.scenario]

    def alert_sender(result):
        alert = build_caregiver_alert(result, topic=args.ntfy_topic)
        return send_ntfy_alert(alert, dry_run=not args.notify)

    result = run_checkin_workflow(
        user_text=scenario["user_text"],
        medicine_name=scenario["medicine_name"],
        day=scenario["day"],
        detected_text=scenario["package_text"],
        user_confirmed=scenario["user_confirmed"],
        return_trace=True,
        alert_sender=alert_sender,
    )

    output = Path(args.json_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    render_trace(result)
    if "caregiver_notification" in result:
        notification = result["caregiver_notification"]
        print(f"Caregiver notification provider: {notification['provider']}")
        print(f"Caregiver notification sent: {notification['sent']}")
        print(f"Caregiver notification URL: {notification['url']}")
    print(f"Saved JSON trace: {output}")


if __name__ == "__main__":
    main()
