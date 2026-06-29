import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from medminder_agent.core_workflow import run_checkin_workflow
from medminder_agent.notification_service import build_caregiver_alert, send_ntfy_alert


ARTIFACT = Path("artifacts/dashboard/latest_dashboard_trace.json")


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


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MedMinder Caregiver Dashboard</title>
  <style>
    :root { color-scheme: light; --ink:#15202b; --muted:#5c6670; --line:#d7dde3; --ok:#1f7a4d; --alert:#b42318; --blue:#175cd3; --bg:#f6f8fa; --panel:#fff; }
    body { margin:0; font-family: Arial, sans-serif; background:var(--bg); color:var(--ink); }
    main { max-width:980px; margin:0 auto; padding:24px; }
    header { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:18px; }
    h1 { font-size:24px; margin:0; }
    .subtle { color:var(--muted); font-size:13px; margin-top:4px; }
    .grid { display:grid; grid-template-columns:320px 1fr; gap:16px; }
    section, aside { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; }
    label { display:block; font-size:13px; font-weight:700; margin:14px 0 6px; }
    select, input { width:100%; box-sizing:border-box; padding:10px; border:1px solid var(--line); border-radius:6px; font-size:14px; }
    button { width:100%; margin-top:14px; border:0; border-radius:6px; padding:11px 12px; font-size:14px; font-weight:700; cursor:pointer; }
    .primary { background:var(--blue); color:white; }
    .secondary { background:#eef2f6; color:var(--ink); }
    .status { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px; border-radius:6px; background:#eef2f6; margin-bottom:14px; }
    .evidence { display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin:14px 0; }
    .metric { border:1px solid var(--line); border-radius:6px; padding:10px; background:#fbfcfd; }
    .metric span { display:block; color:var(--muted); font-size:12px; margin-bottom:5px; }
    .metric strong { font-size:14px; word-break:break-word; }
    .completed { color:var(--ok); }
    .escalated, .blocked_and_escalated, .incomplete_and_escalated { color:var(--alert); }
    ol { padding-left:22px; margin:0; }
    li { margin:0 0 12px; }
    code, pre { font-size:12px; color:var(--muted); }
    pre { white-space:pre-wrap; background:#f8fafc; border:1px solid var(--line); border-radius:6px; padding:10px; }
    @media (max-width: 760px) { .grid, .evidence { grid-template-columns:1fr; } main { padding:14px; } }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>MedMinder Caregiver Dashboard</h1>
      <div class="subtle" id="topic">ntfy topic: medminder-concierge-demo</div>
    </div>
  </header>
  <div class="grid">
    <aside>
      <label for="scenario">Scenario</label>
      <select id="scenario">
        <option value="success">Success</option>
        <option value="wrong-package">Wrong package</option>
        <option value="loose-pill">Loose pill</option>
        <option value="unsafe-dose">Unsafe dose request</option>
        <option value="no-confirmation">No self-confirmation</option>
      </select>
      <label for="ntfyTopic">Caregiver ntfy.sh topic</label>
      <input id="ntfyTopic" value="medminder-concierge-demo">
      <button class="primary" onclick="run(false)">Run check-in</button>
      <button class="secondary" onclick="run(true)">Run + send real alert</button>
      <p class="subtle">The first button executes the workflow in dry-run notification mode. The second publishes an escalation alert to the ntfy topic.</p>
    </aside>
    <section>
      <div class="status"><strong id="final">No check-in run yet</strong><span id="sent"></span></div>
      <p id="reason"></p>
      <div class="evidence">
        <div class="metric"><span>Workflow</span><strong id="workflow">Waiting</strong></div>
        <div class="metric"><span>Notification</span><strong id="notification">Waiting</strong></div>
        <div class="metric"><span>Saved trace</span><strong>artifacts/dashboard/latest_dashboard_trace.json</strong></div>
      </div>
      <ol id="trace"></ol>
      <pre id="payload"></pre>
    </section>
  </div>
</main>
<script>
async function run(send) {
  const scenario = document.getElementById('scenario').value;
  const topic = document.getElementById('ntfyTopic').value.trim() || 'medminder-concierge-demo';
  document.getElementById('topic').textContent = 'ntfy topic: ' + topic;
  document.getElementById('final').textContent = 'Running...';
  document.getElementById('sent').textContent = '';
  document.getElementById('payload').textContent = '';
  try {
    const response = await fetch(`/api/checkin?scenario=${encodeURIComponent(scenario)}&notify=${send ? '1' : '0'}&topic=${encodeURIComponent(topic)}`, {method:'POST'});
    const data = await response.json();
    document.getElementById('final').textContent = data.final_status;
    document.getElementById('final').className = data.final_status;
    document.getElementById('reason').textContent = data.reason;
    document.getElementById('workflow').textContent = `${scenario} -> ${data.final_status}`;
    const notification = data.caregiver_notification;
    document.getElementById('notification').textContent = notification ? (notification.sent ? `sent to ${notification.url}` : `dry-run at ${notification.url}`) : 'no alert needed';
    document.getElementById('sent').textContent = notification ? (notification.sent ? 'alert sent' : 'dry-run alert') : 'no alert';
    document.getElementById('trace').innerHTML = data.trace.map(step => `<li><strong>${step.step}. ${step.agent}</strong> ${step.action} -> ${step.decision}<br><code>${step.output}</code></li>`).join('');
    document.getElementById('payload').textContent = notification ? JSON.stringify(notification, null, 2) : '';
  } catch (error) {
    document.getElementById('final').textContent = 'Dashboard error';
    document.getElementById('reason').textContent = error.message;
  }
}
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, json.dumps({"status": "ok"}), "application/json")
            return
        if self.path == "/" or self.path.startswith("/?"):
            self._send(200, HTML, "text/html")
            return
        self._send(404, "Not found", "text/plain")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/checkin":
            self._send(404, "Not found", "text/plain")
            return

        query = parse_qs(parsed.query)
        scenario_name = query.get("scenario", ["success"])[0]
        notify = query.get("notify", ["0"])[0] == "1"
        topic = query.get("topic", ["medminder-concierge-demo"])[0]
        scenario = SCENARIOS.get(scenario_name, SCENARIOS["success"])

        def alert_sender(result):
            alert = build_caregiver_alert(result, topic=topic)
            return send_ntfy_alert(alert, dry_run=not notify)

        result = run_checkin_workflow(
            user_text=scenario["user_text"],
            medicine_name=scenario["medicine_name"],
            day=scenario["day"],
            detected_text=scenario["package_text"],
            user_confirmed=scenario["user_confirmed"],
            return_trace=True,
            alert_sender=alert_sender,
        )

        ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        self._send(200, json.dumps(result), "application/json")

    def _send(self, status, body, content_type):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"MedMinder dashboard running at http://{host}:{port}")
    print("Install the ntfy phone app and subscribe to topic: medminder-concierge-demo")
    server.serve_forever()


if __name__ == "__main__":
    main()
