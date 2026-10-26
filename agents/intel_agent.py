"""
agents/intel_agent.py
A2A Competitive Intelligence Sub-Agent — market research and competitive analysis.
Broad analysis scope for global market and competitor intelligence.
"""

from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """You are a Competitive Intelligence Analyst inside SovereignCore.
Your role is to help users with:
- Market trend analysis and industry mapping
- Competitor research and SWOT analysis
- Technology landscape evaluation
- Strategic positioning recommendations
- News and signal synthesis

Be analytical, objective, and cite your reasoning. Structure outputs with clear headings."""


class IntelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Intel Analyst",
            specialty="Competitive intelligence, market research, and strategic analysis",
            scopes=[
                "vault:read:all",
                "tavily:search:all"
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
