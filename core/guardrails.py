"""
core/guardrails.py
NeMo Guardrails policy guard — replaces the fictional 'NemoClaw'.
Inspects every user intent before it reaches the model or tools.

In production you can swap this with the full 'nemoguardrails' library:
    pip install nemoguardrails
"""

import re

# ── Dangerous command patterns ────────────────────────────────────────────────
BLOCKED_PATTERNS = [
    r"rm\s+-rf",
    r"format\s+c:",
    r"del\s+/[fqs]",
    r"drop\s+table",
    r"shutdown",
    r"os\.system\(",
    r"subprocess\.call\(",
    r"\beval\(",
    r"\bexec\(",
    r"__import__",
]

# ── Sensitive topics ───────────────────────────────────────────────────────────
BLOCKED_TOPICS = [
    "illegal", "hack", "exploit", "malware", "virus", "phishing",
    "ransomware", "ddos", "sql injection"
]

# ── Write-operation keywords (trigger AG-UI approval gate) ────────────────────
WRITE_KEYWORDS = [
    "save", "write", "delete", "update", "create file",
    "store", "remember", "add to schedule", "record"
]


class NeMoGuardrails:
    """
    Deterministic policy guard that runs BEFORE every model call or tool use.
    Mirrors the role described as 'NemoClaw' in the SovereignCore spec.
    """

    def __init__(self):
        self._compiled = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

    def inspect(self, text: str) -> dict:
        """
        Inspect user input for policy violations.

        Returns:
            {"allowed": bool, "reason": str}
        """
        # 1. Dangerous shell / code patterns
        for pattern in self._compiled:
            if pattern.search(text):
                return {
                    "allowed": False,
                    "reason": "🛡️ NeMo Guardrails blocked: Dangerous command pattern detected."
                }

        # 2. Blocked topics
        text_lower = text.lower()
        for topic in BLOCKED_TOPICS:
            if topic in text_lower:
                return {
                    "allowed": False,
                    "reason": f"🛡️ NeMo Guardrails blocked: Restricted topic detected."
                }

        return {"allowed": True, "reason": "✅ Policy check passed."}

    def requires_approval(self, text: str) -> bool:
        """
        Returns True if the action is a write operation that needs
        human-in-the-loop approval via the AG-UI gate.
        """
        text_lower = text.lower()
        return any(kw in text_lower for kw in WRITE_KEYWORDS)
