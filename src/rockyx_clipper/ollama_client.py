"""Ollama text generation — local models, NO key at all.

Ollama runs on the user's own computer (https://ollama.com): install it,
pull one small model (``ollama pull qwen2.5:3b`` — ~2 GB, runs fine on a
GTX 1650), and the clipper talks to it at http://localhost:11434. No API
key, no account, no expiry, no per-call cost. If Ollama is not running,
this raises a plain-language error and the pipeline falls back to the
built-in local scorer — clips still work.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


def generate_text(prompt: str, system: str = "", max_tokens: int = 4000,
                  temperature: float = 0.7, timeout: int = 300) -> str:
    """One /api/chat call (stream off). Raises on failure."""
    from .settings import get_ollama_host, get_ollama_model

    host = get_ollama_host().rstrip("/")
    model = get_ollama_model()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/chat", data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode("utf-8"))
            msg = err.get("error", str(exc))
        except Exception:
            msg = str(exc)
        raise RuntimeError(f"Ollama HTTP {exc.code}: {msg}") from exc
    except (urllib.error.URLError, ConnectionError, OSError) as exc:
        raise RuntimeError(
            "Ollama is not running on this computer "
            f"({host}) — install it from ollama.com, then run: "
            f"ollama pull {model}") from exc
    try:
        return data["message"]["content"].strip()
    except (KeyError, TypeError):
        raise RuntimeError("Ollama returned no usable reply") from None


def probe() -> str:
    """Harmless smoke test; returns the model's reply."""
    return generate_text("Reply with exactly the word OK.", max_tokens=10, temperature=0)
