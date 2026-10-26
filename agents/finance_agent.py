"""
agents/finance_agent.py
A2A Finance Advisory Sub-Agent — personal finance and investment analysis.
Scoped strictly to finance records and market intelligence.
"""

from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """You are an AI Finance Advisor inside SovereignCore.
Your role is to help users with:
- Personal budget tracking and expense categorization
- Investment analysis and portfolio suggestions
- Savings goals and financial planning
- Debt management strategies
- Market trend awareness

Always remind users: this is AI-generated guidance, not certified financial advice.
Be analytical, data-driven, and clear."""


class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Finance Advisor",
            specialty="Personal finance, budgeting, and investment analysis",
            scopes=[
                "vault:read:finance",
                "vault:write:finance",
                "tavily:search:finance"
            ]
        )

    def process(self, query: str, nemotron_client) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
        result = ""
        for chunk in nemotron_client.stream_chat(messages):
            result += chunk
        return result
