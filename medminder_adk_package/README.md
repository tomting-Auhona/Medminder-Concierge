# MedMinder Concierge

MedMinder Concierge is a safety-first multi-agent medication routine assistant for elderly users and caregivers.

## Course concepts demonstrated

- Multi-agent workflow in the Kaggle notebook
- ADK-style root agent in medminder_agent/agent.py
- MCP server in medminder_mcp_server.py
- Security guardrails in security.py and security_screen.py
- Agent Skill in SKILL.md
- STRIDE threat model
- Local evaluation traces
- Deployability notes

## Safety

This demo uses mock data only.

It does not give medical advice, change dosages, identify loose pills, prove ingestion, send real SMS/calls, or include API keys.

## Setup

pip install -r requirements.txt

python smoke_test.py

python tests/eval/generate_traces.py

## MCP server idea

python medminder_mcp_server.py

## ADK idea

adk run medminder_agent
