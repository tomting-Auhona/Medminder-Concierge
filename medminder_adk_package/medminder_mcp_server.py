try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    FastMCP = None

from medminder_agent.security import security_policy

mcp = FastMCP("medminder-concierge-mcp") if FastMCP else None

def mcp_tool(func):
    return mcp.tool()(func) if mcp else func

MOCK_MEDICATIONS = [
    {"name": "Amlodipine", "dosage": "5mg", "time": "09:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
    {"name": "Metformin", "dosage": "500mg", "time": "20:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
    {"name": "Vitamin D", "dosage": "1000 IU", "time": "10:00", "days": ["Friday"]},
]

@mcp_tool
def get_due_medications(day: str) -> dict:
    due = [m for m in MOCK_MEDICATIONS if day in m["days"]]
    return security_policy.safe_response("success", "Due medicines found.", {"due_medications": due})

@mcp_tool
def check_package_text(expected_name: str, expected_dosage: str, package_text: str) -> dict:
    safe, reason = security_policy.is_safe_user_text(package_text)

    if not safe:
        return security_policy.safe_response("blocked", reason, {"package_match": False})

    clean = package_text.lower().replace(" ", "")

    if "loosepill" in clean or "whitepill" in clean:
        return security_policy.safe_response("blocked", "Loose pill blocked. Original package required.", {"package_match": False})

    match = expected_name.lower().replace(" ", "") in clean and expected_dosage.lower().replace(" ", "") in clean

    if match:
        return security_policy.safe_response("success", "Package matches schedule.", {"package_match": True})

    return security_policy.safe_response("escalate", "Package mismatch. Caregiver review recommended.", {"package_match": False})

@mcp_tool
def simulate_caregiver_alert(reason: str, urgency: str = "medium") -> dict:
    return security_policy.safe_response("success", "Caregiver alert simulated.", {"reason": reason, "urgency": urgency})

if __name__ == "__main__":
    if mcp is None:
        print("MCP package not installed. This file is generated for GitHub review.")
    else:
        mcp.run()
