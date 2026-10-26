"""
core/nemotron.py
NVIDIA Nemotron client via NVIDIA API (OpenAI-compatible).
Endpoint: https://integrate.api.nvidia.com/v1
"""

import os
from openai import OpenAI
from core.tiers import get_tier_config


class NemotronClient:
    """
    Wraps the NVIDIA-hosted Nemotron models using the OpenAI-compatible SDK.
    Automatically selects the correct model based on the user's tier.
    """

    BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(self, tier: str = "free"):
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        if not self.api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "NVIDIA_API_KEY" in st.secrets:
                    self.api_key = str(st.secrets["NVIDIA_API_KEY"]).strip()
            except Exception:
                pass

        self.tier = tier
        tier_config = get_tier_config(tier)
        self.model = tier_config["model"]

        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key=self.api_key if self.api_key else "NO_KEY_SET"
        )

    def chat(self, messages: list, stream: bool = True):
        """Send a chat completion request to NVIDIA Nemotron."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            max_tokens=1024,
            temperature=0.7
        )

    def stream_chat(self, messages: list):
        """
        Stream a chat completion token-by-token.
        Yields string chunks for AG-UI live display.
        """
        if not self.api_key:
            yield "⚠️ NVIDIA_API_KEY is not set. Please add it to your .env file."
            return

        try:
            response = self.chat(messages, stream=True)
            for chunk in response:
                # Skip empty chunks (finish_reason chunks have no choices content)
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            yield f"❌ Nemotron API Error: {str(e)}"
