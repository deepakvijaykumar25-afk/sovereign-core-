"""
core/tiers.py
Tier configuration for SovereignCore.
"""

TIERS = {
    "free": {
        "name": "Free",
        "price": "$0/mo",
        "model": "deepseek-ai/deepseek-v4.1-flash",
        "daily_messages": 30,
        "daily_searches": 10,
        "features": ["Basic vault", "Tavily search (limited)", "Wake Word: Nemo"],
        "security": "Basic Sandbox"
    },
    "core": {
        "name": "Core (Student)",
        "price": "$9.99/mo",
        "model": "deepseek-ai/deepseek-v4.1-flash",
        "daily_messages": -1,
        "daily_searches": 100,
        "features": ["Exam Generator", "Lecture Summarizer", "Habit Tracker", "AI Coach", "Study Schedule"],
        "security": "Standard Sandbox"
    },
    "prime": {
        "name": "Prime (Dev/Biz)",
        "price": "$29.99/mo",
        "model": "deepseek-ai/deepseek-v4.1-flash",
        "daily_messages": -1,
        "daily_searches": -1,
        "features": ["Multi-File AI Coder", "Competitive Intel", "Finance Ledger", "Agent Builder", "All Core features"],
        "security": "NeMo Guardrails Dynamic Firewall"
    },
    "enterprise": {
        "name": "Enterprise",
        "price": "$25/seat/mo",
        "model": "deepseek-ai/deepseek-v4.1-flash",
        "daily_messages": -1,
        "daily_searches": -1,
        "features": ["Shared Memory Spaces", "CEO AI Fleet", "Department Agents", "SSO & Audit", "All Prime features"],
        "security": "Air-Gapped NeMo Zero-Trust"
    }
}


def get_tier_config(tier_name: str) -> dict:
    """Return configuration for the given tier name."""
    return TIERS.get(tier_name, TIERS["free"])
