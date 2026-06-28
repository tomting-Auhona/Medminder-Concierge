# Medminder-Concierge
Safety-first multi-agent medication routine assistant for elderly users and caregivers, with Kaggle demo, ADK/MCP package, Agent Skill, and security guardrails.

## Architecture

MedMinder Concierge uses a safety-first, coordinator-based multi-agent architecture.

The system starts with the senior user, who receives a reminder, shows the original medicine package, and confirms whether they took the medicine.

The interaction layer includes a phone-style Kaggle dashboard prototype and an Antigravity prototype workspace. The Kaggle notebook contains the tested workflow, while Antigravity was used to organize the backend, frontend, and documentation structure.

At the center is the SafetyGuardrailAgent and the MedMinder Coordinator Agent. The safety layer blocks unsafe medication requests such as dosage changes, diagnosis, loose-pill identification, and ingestion-proof claims. The coordinator then routes the check-in through specialist agents.

The specialist agents handle schedule lookup, timing checks, duplicate prevention, package verification, compliance, refusal reason analysis, history tracking, and caregiver escalation.

The final output is either a completed check-in, a caregiver alert, or an updated history/adherence summary.

<img width="1491" height="1055" alt="ChatGPT Image Jun 28, 2026, 12_53_26 PM" src="https://github.com/user-attachments/assets/6fac9b19-61c3-4a95-b14a-d6531d8ba945" />

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
