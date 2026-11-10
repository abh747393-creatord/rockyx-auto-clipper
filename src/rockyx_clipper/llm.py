"""AI provider dispatcher for the scorer.

The scorer (score.py) calls llm.generate_text() and gets whichever
provider the user picked in AI Settings — no per-provider code in the
pipeline:

- gemini: Google Gemini, key from the vault (Muse) or AI Settings.
- deepseek: DeepSeek API, one long-lived key saved once in AI Settings.
- ollama: a local model via Ollama — NO key at all, runs on this computer.
"""
from __future__ import annotations

PROVIDERS = ["gemini", "deepseek", "ollama"]


def active_provider() -> str:
    """The provider from settings; anything unknown falls back to gemini."""
    from .settings import load_settings

    provider = load_settings().get("provider", "gemini")
    return provider if provider in PROVIDERS else "gemini"


def generate_text(prompt: str, system: str = "", max_tokens: int = 4000,
                  temperature: float = 0.7, timeout: int = 120) -> str:
    """One text-generation call through the active provider."""
    provider = active_provider()
    if provider == "deepseek":
        from . import deepseek_client
        return deepseek_client.generate_text(
            prompt, system=system, max_tokens=max_tokens,
            temperature=temperature, timeout=timeout)
    if provider == "ollama":
        from . import ollama_client
        return ollama_client.generate_text(
            prompt, system=system, max_tokens=max_tokens,
            temperature=temperature, timeout=max(timeout, 300))
    from . import gemini_client
    return gemini_client.generate_text(
        prompt, system=system, max_tokens=max_tokens,
        temperature=temperature, timeout=timeout)


def probe() -> str:
    """Harmless smoke test through the active provider."""
    return generate_text("Reply with exactly the word OK.", max_tokens=10, temperature=0)
