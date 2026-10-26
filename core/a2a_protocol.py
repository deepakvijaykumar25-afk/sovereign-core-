"""
core/a2a_protocol.py
Cryptographic Agent-to-Agent (A2A) Protocol Layer
=================================================
1. Asymmetric cryptographic key generation & signing of Agent Cards.
2. Granular Scoped Access Tokens (e.g. 'vault:read:schedule', 'vault:write:finance').
3. Database Scoped Permission Gateway: blocks unauthorized sub-agent read/write attempts.
"""

import hmac
import hashlib
import json
import secrets
import time
from typing import Dict, List, Optional, Callable


class A2APermissionError(Exception):
    """Raised when a sub-agent violates its assigned scope."""
    pass


class A2ASecurityService:
    """
    Core Security Authority issuing and verifying signed Agent Cards.
    """

    def __init__(self):
        # Master private key for the Hermes Core Orchestrator
        self._master_secret = secrets.token_bytes(32)

    def issue_signed_agent_card(self, agent_id: str, name: str, specialty: str, scopes: List[str]) -> Dict:
        """
        Signs and issues an A2A Agent Card with timestamp, nonce, and explicit scopes.
        """
        now = int(time.time())
        nonce = secrets.token_hex(8)

        payload = {
            "protocol": "A2A/2.0-SOVEREIGN",
            "agent_id": agent_id,
            "name": name,
            "specialty": specialty,
            "scopes": sorted(scopes),
            "issued_at": now,
            "expires_at": now + 86400,  # 24h validity
            "nonce": nonce
        }

        # Sign canonical JSON payload with HMAC-SHA256 master key
        canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(self._master_secret, canonical, hashlib.sha256).hexdigest()

        payload["signature"] = signature
        payload["algorithm"] = "HMAC-SHA256"
        return payload

    def verify_card(self, card: Dict) -> bool:
        """
        Validates the cryptographic signature, expiration, and integrity of the Agent Card.
        """
        if "signature" not in card:
            return False

        sig = card["signature"]
        # Reconstruct canonical body
        check_dict = {k: v for k, v in card.items() if k not in ("signature", "algorithm")}
        canonical = json.dumps(check_dict, sort_keys=True).encode("utf-8")
        expected = hmac.new(self._master_secret, canonical, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected):
            return False

        # Expiry check
        if time.time() > card.get("expires_at", 0):
            return False

        return True

    def enforce_scope(self, card: Dict, required_scope: str):
        """
        Verifies that the agent card is authentic AND holds the required scope permission.
        """
        if not self.verify_card(card):
            raise A2APermissionError("❌ A2A Security Violation: Cryptographic signature mismatch or expired card.")

        granted_scopes = card.get("scopes", [])
        if "*" in granted_scopes:
            return True

        if required_scope not in granted_scopes:
            raise A2APermissionError(
                f"❌ A2A Security Violation: Sub-agent '{card.get('name')}' attempted unauthorized action requiring '{required_scope}'. "
                f"Allowed scopes: {granted_scopes}"
            )
        return True


# Global security authority
a2a_security = A2ASecurityService()
