# MedMinder Dashboard Deployment

This package can run locally or as a simple Cloud Run container.

## Local

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

## Caregiver Notification

Install the ntfy phone app and subscribe to a topic such as:

```text
medminder-concierge-demo
```

In the dashboard, run an escalation scenario and choose `Run + send real alert`.

## Safety Boundary

This deployment uses mock data only. It does not send medical advice, change dosages, identify loose pills, prove ingestion, or transmit real patient records.
