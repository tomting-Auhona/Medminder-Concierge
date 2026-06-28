# MedMinder Concierge
Safety-first multi-agent medication routine assistant for elderly users and caregivers, with Kaggle demo, ADK/MCP package, Agent Skill, and security guardrails.

<img width="1774" height="887" alt="MedMinder Concierge" src="https://github.com/user-attachments/assets/5101d96d-7528-49ae-9918-5de0d5da88c6" />

## Architecture

MedMinder Concierge uses a safety-first, coordinator-based multi-agent architecture.

The system starts with the senior user, who receives a reminder, shows the original medicine package, and confirms whether they took the medicine.

The interaction layer includes a phone-style Kaggle dashboard prototype and an Antigravity prototype workspace. The Kaggle notebook contains the tested workflow, while Antigravity was used to organize the backend, frontend, and documentation structure.

At the center is the SafetyGuardrailAgent and the MedMinder Coordinator Agent. The safety layer blocks unsafe medication requests such as dosage changes, diagnosis, loose-pill identification, and ingestion-proof claims. The coordinator then routes the check-in through specialist agents.

The specialist agents handle schedule lookup, timing checks, duplicate prevention, package verification, compliance, refusal reason analysis, history tracking, and caregiver escalation.

The final output is either a completed check-in, a caregiver alert, or an updated history/adherence summary.

<img width="1491" height="1055" alt="architecture" src="https://github.com/user-attachments/assets/b918a0ea-107f-440f-98b5-909ebed6b36c" />

## Why This Project Uses Mock Data

MedMinder Concierge uses mock data intentionally.

Because the project involves medication routines, the demo avoids real patient data, real phone numbers, real caregiver contacts, and real medical records. This keeps the project safe, reproducible, and reviewable.

The mock data still demonstrates the full agent workflow:

- schedule lookup
- package verification
- safety screening
- self-confirmation
- refusal analysis
- caregiver escalation
- history tracking
- trajectory logging
- structured tool-call execution

The system is designed so real services such as Gemini Vision, secure databases, and caregiver notification APIs could be connected later without changing the core safety-first architecture.

## ADK/MCP Status

The fully tested workflow for MedMinder Concierge runs in the Kaggle notebook.

The repository also includes an executable ADK/MCP-style package as a course-aligned extension. This package shows the architectural path toward a local agent development setup and includes deterministic agent traces that can be run without API keys. It is not presented as a fully deployed production system.

The ADK-style root agent file is located at:

```text
medminder_adk_package/medminder_agent/agent.py
```

The MCP server file is located at:

```text
medminder_adk_package/medminder_mcp_server.py
```

The MCP server file demonstrates how specialist agents could expose their capabilities as callable tools to external orchestrators, following the Model Context Protocol pattern covered in the course.

This separation is intentional:

* the Kaggle notebook proves the safe multi-agent workflow
* the ADK/MCP package executes the same safety-first check-in workflow locally
* the MCP file demonstrates how schedule lookup, package verification, caregiver escalation, and history tools could be exposed through a tool interface

## Executable Demo Evidence

For a clearer judge demo, the package includes a scenario runner that executes the real workflow and writes JSON traces.

```bash
cd medminder_adk_package
python demo_runner.py --scenario success
python demo_runner.py --scenario wrong-package
python demo_runner.py --scenario loose-pill
python demo_runner.py --scenario unsafe-dose
python demo_runner.py --scenario no-confirmation
```

Each run prints the agent-by-agent path and saves:

```text
medminder_adk_package/artifacts/demo/latest_demo_trace.json
```

The evaluation script also calls the real workflow in `medminder_agent/core_workflow.py` and saves reviewable traces:

```bash
python tests/eval/generate_traces.py
```

Expected result:

```text
Passed 6/6 real workflow evaluation cases.
```

Generated evidence:

```text
medminder_adk_package/artifacts/traces/generated_traces.json
medminder_adk_package/artifacts/traces/eval_summary.md
```

## How to Run / Setup Instructions

This project can be reviewed in two ways:

1. by opening the main Kaggle notebook, which contains the full tested multi-agent workflow
2. by running the generated ADK/MCP package locally, which shows the repo-ready agent extension

---

### Option 1: Run the Main Notebook

Open the notebook file:

```text
medminder-concierge.ipynb
```

Then run all cells from top to bottom.

The notebook demonstrates:

* the full MedMinder multi-agent workflow
* safety guardrails
* medication schedule lookup
* package verification simulation
* user self-confirmation
* caregiver escalation
* refusal reason analysis
* history and adherence tracking
* test cases and evaluation results
* phone-style dashboard prototype
* ADK/MCP package generation

Expected result:

```text
Main coordinator tests: 10/10 passed
Course-inspired trace evaluation: 5/5 passed
Security smoke test: passed
```

The notebook uses mock data only. No real patient data, API keys, SMS, or medical records are required.

---

### Option 2: Run the ADK/MCP Package Locally

The generated course-aligned package is inside:

```text
medminder_adk_package/
```

From the repository root, move into the package folder:

```bash
cd medminder_adk_package
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the smoke test:

```bash
python smoke_test.py
```

Run the trace evaluation:

```bash
python tests/eval/generate_traces.py
```

Expected result:

```text
Smoke test passed.
Passed 6/6 real workflow evaluation cases.
```

---

### ADK and MCP Commands

The package includes an ADK-style root agent and a local MCP server file.

ADK-style agent file:

```text
medminder_adk_package/medminder_agent/agent.py
```

MCP server file:

```text
medminder_adk_package/medminder_mcp_server.py
```

Optional local MCP command:

```bash
python medminder_mcp_server.py
```

Optional ADK command:

```bash
adk run medminder_agent
```

These files are included as a course-aligned extension. The main tested workflow is in the Kaggle notebook.

---

### Files to Review

Important files for reviewing:

```text
README.md
medminder-concierge.ipynb
architecture_diagram.png
submission.csv
medminder_evaluation_results.csv
STATE_MEMORY.md
PRODUCTION_READINESS.md
medminder_adk_package/
```

Inside `medminder_adk_package/`, the most important files are:

```text
medminder_agent/agent.py
medminder_agent/security.py
medminder_agent/security_screen.py
medminder_agent/skills/medminder-safe-checkin/SKILL.md
medminder_mcp_server.py
tests/eval/generate_traces.py
tests/eval/datasets/medminder-eval-dataset.json
threat_model.md
AGENTS_CLI_NOTES.md
MCP_CONFIG_NOTES.md
COURSE_ALIGNMENT.md
```

---

### Safety Note

MedMinder Concierge is a safety-first prototype.

It does not:

* give medical advice
* prescribe medicine
* change dosages
* identify loose pills
* prove ingestion
* use real patient data
* send real SMS or calls
* include API keys or passwords

The purpose of this submission is to demonstrate a safe, modular, multi-agent medication routine workflow using mock data.


## State, Memory, Agent Skills, and Production Readiness

MedMinder uses lightweight structured state instead of storing long free-form conversations.

During a check-in, the coordinator tracks the selected medication, package verification result, user confirmation, safety flags, escalation status, and final outcome.

For longer-term memory, the `HistoryTrackerAgent` stores completion records across days and calculates adherence score, missed doses, missed streaks, and risk summaries.

This keeps context small and privacy-aware. Instead of sending full history into every agent step, the system uses compact summaries such as the current medicine, current safety status, and recent adherence pattern.

The generated ADK/MCP package also includes an Agent Skill file at:

```text
medminder_adk_package/medminder_agent/skills/medminder-safe-checkin/SKILL.md
```
This documents the safe medication check-in workflow for reuse in an agentic development setup.

More details are available in:

* `STATE_MEMORY.md`
* `PRODUCTION_READINESS.md`

The notebook also includes fictional Gemini Vision OCR mocking and OpenTelemetry-style trajectory logs. The OCR mock simulates package text extraction from a medicine label, while the trajectory logs show how the coordinator routes a check-in through safety screening, schedule lookup, package verification, refusal analysis, caregiver escalation, and history tracking.

Generated files:

- `medminder_agent_trajectory_logs.csv`
- `medminder_agent_trajectory_logs.json`

The notebook also includes a structured tool-call demo through `MedMinderToolKit`, which simulates ADK/MCP-style tool binding. It prints tool-call payloads, validates allowlisted tools, executes schedule lookup, package text checking, caregiver alert simulation, and history summary generation.

Generated files:

- `medminder_structured_tool_call_logs.csv`
- `medminder_structured_tool_call_logs.json`

The current project is a Kaggle-tested prototype with a repo-ready ADK/MCP extension. A live deployment is not included because the project is safety-first and uses mock medication data only. A future production version could run as a hosted API with health checks, structured logs, safety event tracking, caregiver authentication, and secure storage.

## Limitations and Future Work

Current limitations:

- no real patient data
- no real medicine image upload in the demo
- no real medical decision-making

Future improvements could include:

- Gemini Vision for reading original medicine packaging
- Firebase or Supabase for secure storage
- Twilio or WhatsApp caregiver alerts
- authentication for caregivers
- doctor-approved medication schedule import
