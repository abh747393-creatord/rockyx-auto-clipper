"""Custom model provider — any OpenAI-compatible server.

This is for the user's own model: Ollama on his own computer, LM Studio,
or any other OpenAI-compatible endpoint. Settings (AI Settings card):
  custom_base_url — e.g. http://localhost:11434/v1 (Ollama) or
                     http://localhost:1234/v1 (LM Studio)
  custom_model    — e.g. qwen2.5:3b
  custom_api_key  — optional; sent as a Bearer token when set. Local
                    servers usually accept any key (or none at all).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


def generate_text(prompt: str, system: str = "", max_tokens: int = 4000,
                  temperature: float = 0.7, timeout: int = 300) -> str:
    """One POST {base_url}/chat/completions call. Raises on failure."""
    from .settings import get_custom_api_key, get_custom_base_url, get_custom_model

    base_url = get_custom_base_url().rstrip("/")
    model = get_custom_model()
    key = get_custom_api_key()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(
        f"{base_url}/chat/completions", data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode("utf-8"))
            msg = err.get("error", {}).get("message", str(exc))
        except Exception:
            msg = str(exc)
        raise RuntimeError(f"Custom model HTTP {exc.code}: {msg}") from exc
    except (urllib.error.URLError, ConnectionError, OSError) as exc:
        raise RuntimeError(
            f"Could not reach the custom model at {base_url} — is the "
            f"server running? (Ollama: run `ollama serve`; LM Studio: "
            f"start the local server)") from exc
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Custom model returned no usable reply") from None


def probe() -> str:
    """Harmless smoke test; returns the model's reply."""
    return generate_text("Reply with exactly the word OK.", max_tokens=10, temperature=0)
