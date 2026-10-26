"""
core/tavily_search.py
Tavily MCP Search — real-time live web intelligence layer.
Powers the agent's citation engine with zero hallucination.
"""

import os
from tavily import TavilyClient


class TavilyMCPSearch:
    """
    Wraps the Tavily Search API as an MCP-style tool.
    Falls back gracefully when the API key is not configured.
    """

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY", "")
        if api_key:
            self.client = TavilyClient(api_key=api_key)
            self.available = True
        else:
            self.client = None
            self.available = False

    def search(self, query: str, max_results: int = 5) -> list:
        """
        Run a live web search.

        Returns a list of dicts: [{"title", "url", "content"}, ...]
        """
        if not self.available:
            return [{
                "title": "Tavily not configured",
                "url": "",
                "content": "Set TAVILY_API_KEY in your .env to enable live web search."
            }]

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_answer=True
            )
            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", "No title"),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:400]
                })
            return results

        except Exception as e:
            return [{"title": "Search Error", "url": "", "content": str(e)}]
