"""Gemini text generation via the registered custom.gemini vault credential.

Same credential pattern as gemini_tts.py / gemini_generate.py: the key is
never in this file, in arguments, in environment variables or in logs.
The helper asks authd for an hsurr: surrogate and puts it in the
x-goog-api-key header; the real key is swapped in only on an approved
request to generativelanguage.googleapis.com.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
try:
    from dynamic_credentials import add_surrogate_to_request, read_json_response
except Exception:  # pragma: no cover - running outside Muse (e.g. Rocky's PC)
    add_surrogate_to_request = None  # type: ignore
    read_json_response = None  # type: ignore

ALLOWED_HOSTS = ["generativelanguage.googleapis.com"]
ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# 2026-11-10 (verified live): gemini-2.5-flash and gemini-2.0-flash return
# HTTP 404 "no longer available" — only gemini-3.8-flash is current.
MODELS = ["gemini-3.8-flash"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def _open(request, timeout=120):
    return urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout)


def generate_text(prompt: str, system: str = "", max_tokens: int = 4000,
                  temperature: float = 0.7, timeout: int = 120) -> str:
    """One generateContent call. Tries MODELS in order; raises on failure.

    On Rocky's own PC (outside Muse) this needs a Gemini API key — pasted once
    in the web UI's AI Settings (saved to ~/.rockyx/settings.json) or set as
    the GEMINI_API_KEY env var. The vault path is used when available.
    """
    last_err: Exception | None = None
    for model in MODELS:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        if system:
            payload["system_instruction"] = {"parts": [{"text": system}]}
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            ENDPOINT_TEMPLATE.format(model=model),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            if add_surrogate_to_request is not None:
                add_surrogate_to_request(request, "custom.gemini", allowed_hosts=ALLOWED_HOSTS)
            else:
                from .settings import get_gemini_key
                key = get_gemini_key()
                if not key:
                    raise RuntimeError(
                        "No Gemini API key set — paste one in AI Settings "
                        "in the web UI, or set the GEMINI_API_KEY env var")
                request.add_header("x-goog-api-key", key)
            with _open(request, timeout=timeout) as response:
                data = read_json_response(response) if read_json_response else json.loads(response.read())
        except urllib.error.HTTPError as exc:
            try:
                err = json.loads(exc.read().decode("utf-8"))
                msg = err.get("error", {}).get("message", str(exc))
            except Exception:
                msg = str(exc)
            last_err = RuntimeError(f"Gemini HTTP {exc.code}: {msg}")
            continue
        except Exception as exc:  # noqa: BLE001 - network/credential errors, try next model
            last_err = exc
            continue
        if "error" in data:
            last_err = RuntimeError(f"Gemini error: {data['error'].get('message', 'unknown')}")
            continue
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError):
            last_err = RuntimeError("Gemini returned no usable reply")
            continue
    raise RuntimeError(f"Gemini failed on all models: {last_err}")


def probe() -> str:
    """Harmless smoke test; returns the model's reply."""
    return generate_text("Reply with exactly the word OK.", max_tokens=10, temperature=0)
