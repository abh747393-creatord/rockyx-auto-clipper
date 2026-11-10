"""DeepSeek text generation (OpenAI-compatible API).

DeepSeek is the low-cost, long-lived-key alternative to Gemini: one API key
from https://platform.deepseek.com, saved once in AI Settings — it does not
expire the way the OAuth-style token Rocky pasted does, and it is very
cheap (~$0.14/1M input tokens for deepseek-chat). Endpoint:
https://api.deepseek.com/v1/chat/completions, model deepseek-chat.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def generate_text(prompt: str, system: str = "", max_tokens: int = 4000,
                  temperature: float = 0.7, timeout: int = 120) -> str:
    """One chat-completions call. Raises on failure (auth, rate limit, ...)."""
    from .settings import get_deepseek_key

    key = get_deepseek_key()
    if not key:
        raise RuntimeError(
            "No DeepSeek API key set — paste one in AI Settings in the web "
            "UI (provider: DeepSeek), or set the DEEPSEEK_API_KEY env var")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode("utf-8"))
            msg = err.get("error", {}).get("message", str(exc))
        except Exception:
            msg = str(exc)
        raise RuntimeError(f"DeepSeek HTTP {exc.code}: {msg}") from exc
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("DeepSeek returned no usable reply") from None


def probe() -> str:
    """Harmless smoke test; returns the model's reply."""
    return generate_text("Reply with exactly the word OK.", max_tokens=10, temperature=0)
