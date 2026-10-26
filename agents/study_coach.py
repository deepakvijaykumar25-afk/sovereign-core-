"""
agents/study_coach.py
A2A Study Coach Sub-Agent — academic learning and exam preparation.
Scoped strictly to schedule management and academic search.
"""

from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """You are an expert AI Study Coach inside SovereignCore.
Your role is to help students with:
- Personalized study schedules and planning
- Exam preparation strategies and practice questions
- Lecture and textbook summarization
- Habit, focus, and energy tracking
- Spaced-repetition and active-recall techniques

Be specific, actionable, and encouraging. Keep responses concise and structured."""


class StudyCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Study Coach",
            specialty="Academic learning, exam preparation, and habit tracking",
            scopes=[
                "vault:read:schedule",
                "vault:write:schedule",
                "tavily:search:academic"
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
