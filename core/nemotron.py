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

    def chat(self, messages: list, stream: bool = True, model_override: str = None):
        """Send a chat completion request to NVIDIA Nemotron with fallback."""
        model_to_use = model_override or self.model
        return self.client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            stream=stream,
            max_tokens=1024,
            temperature=0.7
        )

    def stream_chat(self, messages: list):
        """
        Stream a chat completion token-by-token.
        Yields string chunks for AG-UI live display with automatic fallback.
        """
        if not self.api_key or self.api_key == "NO_KEY_SET":
            yield "⚠️ NVIDIA_API_KEY is not configured in Secrets. Please add it to your Streamlit Cloud secrets."
            return

        candidate_models = [
            self.model,
            "nvidia/nemotron-3.5-lightning-30b-a3b",
            "meta/llama-3.1-70b-instruct"
        ]
        # Deduplicate while preserving order
        unique_candidates = list(dict.fromkeys(candidate_models))

        last_error = None
        for candidate in unique_candidates:
            try:
                response = self.chat(messages, stream=True, model_override=candidate)
                for chunk in response:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                # If stream succeeded, finish
                return
            except Exception as e:
                err_str = str(e)
                last_error = err_str
                # If 403 (forbidden/unauthorized model) or 404 (not found), try next model
                if "403" in err_str or "404" in err_str:
                    continue
                else:
                    yield f"❌ Nemotron API Error: {err_str}"
                    return

        if last_error:
            yield f"❌ Nemotron API Error: {last_error}"
