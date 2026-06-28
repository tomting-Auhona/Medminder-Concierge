# Agent Skills, State, and Memory

MedMinder Concierge uses lightweight structured state instead of storing long free-form conversations.

This is important because a medication routine assistant must remember enough context to avoid unsafe or repeated actions, but it should not store unnecessary private information.

## Why State and Memory Matter

Medication support is not just a one-step task.
The system needs to know:

* which medicine is due
* whether the package was shown
* whether the package matched the stored schedule
* whether the user confirmed completion
* whether the check-in was already completed
* whether the case should be escalated to a caregiver
* whether there are missed-dose patterns over time

Instead of saving full conversations, MedMinder stores only the minimum structured information needed for safe routine support.

## State Objects Used

The main Kaggle notebook uses structured state through:

* `MedMinderState`
* `CompletionRecord`
* `conversation_log`
* `escalation_log`
* `HistoryTrackerAgent`

## Short-Term State

During one medication check-in, the coordinator tracks:

1. the selected scheduled medicine
2. whether packaging was seen
3. whether the package matched the schedule
4. whether the user confirmed taking the medicine
5. safety flags
6. escalation status
7. final workflow outcome

This short-term state helps the coordinator decide whether to complete the check-in or escalate to a caregiver.

## Long-Term Memory

Long-term memory is simulated through the `HistoryTrackerAgent`.

It stores completion records across days and calculates:

* adherence score
* missed doses
* missed streaks
* risk summary

This helps the system identify patterns such as repeated missed check-ins.

## What Is Stored

The system stores only minimal mock information needed for the demo:

* patient display name
* selected medication
* check-in date and time
* final check-in status
* package verification result
* user confirmation result
* safety flags
* escalation messages
* completion records over time

## What Is Not Stored

The system does not store:

* real patient data
* real phone numbers
* real medical records
* real caregiver contact details
* API keys
* passwords
* unnecessary long conversations

## Token and Context Strategy

MedMinder avoids sending full history into every agent step.

Instead, it uses compact context:

* current scheduled medicine
* current package verification status
* current confirmation status
* latest safety flags
* recent adherence summary
* caregiver escalation status

Older events are stored as structured records and summarised only when needed.

This keeps the active context small, reduces token usage, protects privacy, and helps the agents stay focused on the current medication routine.

## Agent Skill

The generated package includes an Agent Skill file:

```text
medminder_adk_package/medminder_agent/skills/medminder-safe-checkin/SKILL.md
```

This skill defines the safe check-in workflow:

1. check the stored schedule
2. ask for the original medicine package
3. verify package text
4. ask for self-confirmation
5. complete only if safe
6. escalate unsafe or incomplete cases

## Safety Benefit

This state and memory design supports safety because the system can:

* prevent duplicate check-ins
* detect missed streaks
* avoid storing unnecessary private information
* keep only relevant medication routine context
* escalate when the state shows uncertainty or risk

MedMinder’s memory is therefore designed to be small, structured, explainable, and privacy-aware.
