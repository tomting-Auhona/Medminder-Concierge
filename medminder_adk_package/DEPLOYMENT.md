# MedMinder Dashboard Deployment

This package contains a small deployable caregiver dashboard for the MedMinder Concierge demo. It runs the same deterministic safety-first workflow used by the CLI and evaluation scripts, then writes the executed trace to disk and optionally sends a real phone notification through ntfy.sh.

The dashboard is intentionally lightweight so judges can run it without API keys, accounts, or private patient data.

## What the Dashboard Does

- Executes `medminder_agent/core_workflow.py` for a selected scenario.
- Shows the agent trace: safety screen, schedule lookup, package verification, compliance, and escalation.
- Writes the latest dashboard run to `artifacts/dashboard/latest_dashboard_trace.json`.
- Builds a caregiver alert payload for escalation cases.
- Sends a real ntfy phone notification only when the reviewer chooses `Run + send real alert`.
- Exposes `/healthz` for local or Cloud Run health checks.

## Local Run

```bash
python caregiver_dashboard.py
```

Open:

```text
http://127.0.0.1:8765
```

Health check:

```text
http://127.0.0.1:8765/healthz
```

## Notification Modes

The dashboard has two execution modes:

```text
Run check-in
```

This runs the workflow and keeps notifications in dry-run mode. It still returns the exact ntfy payload and URL that would be used.

```text
Run + send real alert
```

This runs the workflow and sends an ntfy notification when the result is an escalation, blocked escalation, or incomplete check-in.

Install the ntfy phone app and subscribe to:

```text
medminder-concierge-demo
```

You can also type another topic in the dashboard field. For a CLI proof, run:

```bash
python demo_runner.py --scenario wrong-package --notify --ntfy-topic medminder-concierge-demo
```

Without `--notify`, the CLI also uses dry-run mode.

## Cloud Run Container Path

The included `Dockerfile` runs the dashboard on `HOST=0.0.0.0` and `PORT=8080`, which matches Cloud Run conventions.

Example manual deployment command:

```bash
gcloud run deploy medminder-concierge-dashboard \
  --source . \
  --region YOUR_REGION \
  --allow-unauthenticated
```

For a private demo, remove `--allow-unauthenticated` and use authenticated access.

Useful environment variables:

```text
HOST=0.0.0.0
PORT=8080
MEDMINDER_NTFY_TOPIC=medminder-concierge-demo
```

Cloud Run will provide `PORT` automatically. The app also works locally with the default `127.0.0.1:8765`.

## Reviewer Verification Checklist

1. Run `python smoke_test.py` and confirm `Smoke test passed.`
2. Run `python tests/eval/generate_traces.py` and confirm all six evaluation cases pass.
3. Start `python caregiver_dashboard.py`.
4. Open `http://127.0.0.1:8765`.
5. Select `Wrong package` or `Loose pill`.
6. Click `Run check-in` to see the executed trace and dry-run ntfy payload.
7. Subscribe the phone app to `medminder-concierge-demo`, then click `Run + send real alert` for a real notification.

## Safety Boundary

This deployment uses mock data only. It does not send medical advice, change dosages, identify loose pills, prove ingestion, or transmit real patient records. The ntfy message contains only demo text generated from the mock workflow result.

This is not a production medical system. A production version would need caregiver authentication, patient consent, secure storage, audit logging, rate limiting, private notification topics, and clinical review.
