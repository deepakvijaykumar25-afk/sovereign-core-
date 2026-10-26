"""
core/tavily_advanced.py
High-Impact Tavily Implementations for SovereignCore (Hackathon Prize Engine)
=============================================================================
1. Context-Aware Search Routing: Auto-classifies intent (code/tech, news, finance, academic, general)
   and routes queries with customized search depths, topics, and domain filters.
2. Zero-Hallucination Guardrails: Extraction matrix comparing model assertions against retrieved
   Tavily URLs/content. If factual grounding is below threshold, triggers self-correction loop.
"""

import os
import re
from typing import Dict, List, Tuple
from tavily import TavilyClient


# ── DOMAIN ROUTING MAPS ────────────────────────────────────────────────────────
TECHNICAL_DOMAINS = [
    "github.com", "stackoverflow.com", "developer.nvidia.com", 
    "docs.nvidia.com", "python.org", "pypi.org", "learn.microsoft.com"
]

NEWS_DOMAINS = [
    "reuters.com", "bloomberg.com", "techcrunch.com", "theverge.com", 
    "arstechnica.com", "bbc.com", "apnews.com"
]

FINANCE_DOMAINS = [
    "bloomberg.com", "reuters.com", "finance.yahoo.com", "cnbc.com", 
    "sec.gov", "marketwatch.com", "ft.com"
]

ACADEMIC_DOMAINS = [
    "arxiv.org", "scholar.google.com", "ieee.org", "nature.com", "acm.org"
]


class ContextAwareTavilyRouter:
    """
    Classifies user intent and tunes Tavily parameters dynamically.
    """

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "TAVILY_API_KEY" in st.secrets:
                    api_key = str(st.secrets["TAVILY_API_KEY"]).strip()
            except Exception:
                pass
        self.client = TavilyClient(api_key=api_key) if api_key else None

    def classify_intent(self, query: str) -> str:
        """
        Classifies query intent into:
        - 'technical' (code, error traces, libraries, APIs)
        - 'news' (current events, recent announcements, what happened)
        - 'finance' (stock, budget, crypto, market cap, inflation)
        - 'academic' (research papers, theorem, math, biology, lab)
        - 'general'
        """
        q = query.lower()

        # Technical patterns
        if any(w in q for q in ["error", "traceback", "exception", "code", "bug", "python", "api", "pip", "compile", "docker", "nvidia", "sdk", "cuda", "nemotron"]):
            return "technical"

        # News / recent events
        if any(w in q for q in ["news", "latest", "today", "yesterday", "announced", "recent", "breaking", "update", "this week"]):
            return "news"

        # Financial queries
        if any(w in q for q in ["stock", "price", "market", "nasdaq", "crypto", "bitcoin", "earnings", "budget", "invest", "dividend", "inflation"]):
            return "finance"

        # Academic / Research
        if any(w in q for q in ["paper", "arxiv", "theorem", "algorithm", "study", "syllabus", "experiment", "proof"]):
            return "academic"

        return "general"

    def search_routed(self, query: str, max_results: int = 5) -> Dict:
        """
        Executes an intent-optimized Tavily search with domain and topic filters.
        """
        intent = self.classify_intent(query)
        if not self.client:
            return {
                "intent": intent,
                "routed_domains": [],
                "results": [{
                    "title": "Tavily API Key Required",
                    "url": "https://tavily.com",
                    "content": "Add your TAVILY_API_KEY in .env to execute live context-aware queries."
                }],
                "topic": "general"
            }

        kwargs = {"query": query, "max_results": max_results, "include_answer": True}

        # Apply context-aware routing filters
        if intent == "technical":
            kwargs["search_depth"] = "advanced"
            kwargs["include_domains"] = TECHNICAL_DOMAINS
            topic = "general"
        elif intent == "news":
            kwargs["topic"] = "news"
            kwargs["days"] = 7
            kwargs["include_domains"] = NEWS_DOMAINS
            topic = "news"
        elif intent == "finance":
            kwargs["search_depth"] = "advanced"
            kwargs["include_domains"] = FINANCE_DOMAINS
            topic = "finance"
        elif intent == "academic":
            kwargs["search_depth"] = "advanced"
            kwargs["include_domains"] = ACADEMIC_DOMAINS
            topic = "academic"
        else:
            kwargs["search_depth"] = "basic"
            topic = "general"

        try:
            res = self.client.search(**kwargs)
            results = []
            for item in res.get("results", []):
                results.append({
                    "title": item.get("title", "Untitled"),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")[:500]
                })
            return {
                "intent": intent,
                "routed_domains": kwargs.get("include_domains", ["Global Web"]),
                "topic": topic,
                "answer": res.get("answer", ""),
                "results": results
            }
        except Exception as e:
            return {
                "intent": intent,
                "routed_domains": [],
                "results": [{"title": "Search Error", "url": "", "content": str(e)}],
                "topic": "error"
            }


class ZeroHallucinationGuardrail:
    """
    Verifies that claims made by local/serverless Nemotron models are grounded
    in Tavily's retrieved search extraction matrix.
    """

    @staticmethod
    def extract_key_assertions(text: str) -> List[str]:
        """Splits model response into sentence assertions."""
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    @classmethod
    def verify_grounding(cls, draft_response: str, tavily_results: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Builds a verification matrix.
        Returns:
            grounding_score (0.0 to 1.0),
            matrix: list of {"assertion": str, "grounded": bool, "matched_source": str}
        """
        if not tavily_results:
            return 1.0, []

        corpus = " ".join([r.get("content", "").lower() for r in tavily_results])
        assertions = cls.extract_key_assertions(draft_response)

        if not assertions:
            return 1.0, []

        grounded_count = 0
        matrix = []

        for statement in assertions:
            # Extract meaningful words (3+ chars, alphanumeric)
            tokens = [t.lower() for t in re.findall(r'\b[a-zA-Z0-9]{3,}\b', statement)]
            if not tokens:
                continue

            matches = sum(1 for t in tokens if t in corpus)
            ratio = matches / len(tokens)
            is_grounded = ratio >= 0.40  # 40% lexical overlap with extracted matrix

            # Find best matched source URL
            best_url = "None"
            if is_grounded:
                grounded_count += 1
                for r in tavily_results:
                    if any(t in r.get("content", "").lower() for t in tokens[:3]):
                        best_url = r.get("url", "Extracted Matrix")
                        break

            matrix.append({
                "assertion": statement[:120] + ("..." if len(statement) > 120 else ""),
                "grounded": is_grounded,
                "matched_source": best_url
            })

        score = round(grounded_count / max(len(matrix), 1), 2)
        return score, matrix

    @classmethod
    def build_self_correction_prompt(cls, draft_response: str, ungrounded_assertions: List[str], tavily_results: List[Dict]) -> str:
        """Constructs a strict self-correction prompt for Nemotron."""
        sources_text = "\n".join([f"- [{r.get('title')}]: {r.get('content')}" for r in tavily_results[:3]])
        ungrounded_text = "\n".join([f"- {a}" for a in ungrounded_assertions])

        return (
            "ZERO-HALLUCINATION GUARDRAIL ACTIVATED.\n"
            "The following assertions in your previous response could not be verified by live web extracts:\n"
            f"{ungrounded_text}\n\n"
            "VERIFIED EXTRACTIONS MATRIX:\n"
            f"{sources_text}\n\n"
            "TASK: Rewrite your answer using ONLY the verified facts from the extraction matrix above. "
            "Remove all unsubstantiated claims and provide clear, truthful explanations."
        )
