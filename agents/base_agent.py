"""
agents/base_agent.py
Base A2A Agent — generates cryptographically signed Agent Cards
following the Agent2Agent (A2A/2.0) protocol spec.
"""

import uuid
from typing import List, Dict
from core.a2a_protocol import a2a_security


class BaseAgent:
    """
    Base class for all SovereignCore sub-agents.
    Each agent holds cryptographically signed scopes enforced at runtime.
    """

    def __init__(self, name: str, specialty: str, scopes: List[str] = None):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.specialty = specialty
        self.scopes = scopes or ["vault:read:general"]
        self._card = None

    def get_agent_card(self) -> Dict:
        """
        Retrieves or issues an authenticated, signed A2A Agent Card.
        """
        if not self._card:
            self._card = a2a_security.issue_signed_agent_card(
                agent_id=self.agent_id,
                name=self.name,
                specialty=self.specialty,
                scopes=self.scopes
            )
        return self._card

    def process(self, query: str, nemotron_client) -> str:
        """Override in each sub-agent to handle the delegated query."""
        raise NotImplementedError("Subclasses must implement process()")
