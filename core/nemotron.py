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

    def get_available_models(self) -> list:
        """Fetch active model IDs directly from the NVIDIA API."""
        if not self.api_key or self.api_key == "NO_KEY_SET":
            return []
        try:
            res = self.client.models.list()
            return [m.id for m in res.data]
        except Exception:
            return []

    def chat(self, messages: list, stream: bool = True, model_override: str = None):
        """Send a chat completion request to NVIDIA endpoint."""
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
        Yields string chunks for AG-UI live display with robust multi-model fallback.
        """
        if not self.api_key or self.api_key == "NO_KEY_SET":
            yield "⚠️ NVIDIA_API_KEY is not configured in Secrets. Please add it to your Streamlit Cloud secrets."
            return

        # Broad candidate list across Nemotron, Meta, DeepSeek, Mistral, and Qwen on NVIDIA NIM
        candidate_models = [
            self.model,
            "deepseek-ai/deepseek-r1",
            "meta/llama-3.3-70b-instruct",
            "mistralai/mistral-7b-instruct-v0.3",
            "qwen/qwen2.5-7b-instruct",
            "google/gemma-2-9b-it",
            "nvidia/nemotron-4-340b-instruct",
            "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        ]

        # Dynamically prepend any live models found on this account
        try:
            live_models = self.get_available_models()
            if live_models:
                # Put active models from account at the front
                candidate_models = live_models[:5] + candidate_models
        except Exception:
            pass

        unique_candidates = list(dict.fromkeys(candidate_models))

        last_error = None
        for candidate in unique_candidates:
            try:
                response = self.chat(messages, stream=True, model_override=candidate)
                yielded_any = False
                for chunk in response:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                        yielded_any = True
                if yielded_any:
                    return
            except Exception as e:
                err_str = str(e)
                last_error = f"{candidate} -> {err_str}"
                # If deprecated (410), forbidden (403), not found (404), or bad request (400), try next candidate
                if any(code in err_str for code in ["410", "403", "404", "400"]):
                    continue
                else:
                    yield f"❌ Nemotron API Error: {err_str}"
                    return

        if last_error:
            yield f"❌ All candidate models failed. Last error: {last_error}"
