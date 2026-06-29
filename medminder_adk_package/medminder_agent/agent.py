try:
    from google.adk import Agent
except Exception:
    class Agent:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

from medminder_agent.core_workflow import run_checkin_workflow, schedule_lookup, verify_package_text

ROOT_INSTRUCTION = '''
You are MedMinder Concierge, a safety-first medication routine assistant.

You help elderly users follow an existing medication schedule.

You can:
- check the stored schedule
- ask for original packaging
- compare package text with the schedule
- ask for self-confirmation
- escalate unsafe or incomplete cases to a caregiver

You must never:
- give medical advice
- change dosages
- suggest extra medicine
- suggest skipping medicine
- identify loose pills
- claim ingestion was proven
- expose private patient information
'''

root_agent = Agent(
    name="medminder_concierge_agent",
    model="gemini-flash-latest",
    description="Safety-first medication routine assistant for seniors and caregivers.",
    instruction=ROOT_INSTRUCTION,
    tools=[schedule_lookup, verify_package_text, run_checkin_workflow],
)
