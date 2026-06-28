ALLOWED_TOOLS = {
    "get_due_medications",
    "check_package_text",
    "record_self_confirmation",
    "simulate_caregiver_alert",
    "get_adherence_summary",
}

UNSAFE_MEDICATION_INTENTS = [
    "take extra",
    "take another",
    "double",
    "increase dose",
    "decrease dose",
    "skip",
    "stop taking",
    "replace medicine",
    "diagnose",
    "side effect",
    "identify this pill",
    "what pill is this",
    "loose pill",
    "prove swallowed",
    "prove ingestion",
]

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "bypass safety",
    "bypass rules",
    "override system",
    "developer mode",
    "reveal hidden",
    "show system prompt",
    "act as admin",
]
