"""Local AI settings for the Rockyx Auto-Clipper.

The user pastes their Gemini API key once in the web UI (AI Settings card)
instead of setting an environment variable. The key lives ONLY on this
machine, in a JSON file OUTSIDE the project folder, so it can never be
committed or pushed to GitHub by accident:

    ~/.rockyx/settings.json        (Linux/macOS)
    C:\\Users\\<name>\\.rockyx\\settings.json   (Windows)

Permissions are tightened to owner-only (0600) on POSIX. The key is never
printed, logged, or returned whole by any API — the UI only ever sees a
masked form (first 4 + last 4 characters).

Key lookup order for the Gemini scorer:
    1. saved settings file (what the UI writes)
    2. GEMINI_API_KEY environment variable
    3. (on Muse's VM only) the vault credential via gemini_client

Providers (v0.1.7): the AI Settings card picks one provider for the
scorer — "gemini" (default), "deepseek" (one long-lived API key, saved
once), or "ollama" (a local model, no key at all). The DeepSeek key has
the same lookup order (settings, then DEEPSEEK_API_KEY); the Ollama model
and host are settings-only.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

SETTINGS_DIR = Path.home() / ".rockyx"
SETTINGS_PATH = SETTINGS_DIR / "settings.json"

SCORERS = ["auto", "gemini", "heuristic", "local-ml"]
PROVIDERS = ["gemini", "deepseek", "ollama"]
DEFAULTS = {"gemini_api_key": "", "scorer": "auto", "provider": "gemini",
            "deepseek_api_key": "", "ollama_model": "qwen2.5:3b",
            "ollama_host": "http://localhost:11434"}


def load_settings() -> dict:
    """Read the settings file; missing/corrupt file -> defaults."""
    data = dict(DEFAULTS)
    try:
        if SETTINGS_PATH.exists():
            raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                if isinstance(raw.get("gemini_api_key"), str):
                    data["gemini_api_key"] = raw["gemini_api_key"].strip()
                if isinstance(raw.get("deepseek_api_key"), str):
                    data["deepseek_api_key"] = raw["deepseek_api_key"].strip()
                if raw.get("scorer") in SCORERS:
                    data["scorer"] = raw["scorer"]
                if raw.get("provider") in PROVIDERS:
                    data["provider"] = raw["provider"]
                if isinstance(raw.get("ollama_model"), str) and raw["ollama_model"].strip():
                    data["ollama_model"] = raw["ollama_model"].strip()
                if isinstance(raw.get("ollama_host"), str) and raw["ollama_host"].strip():
                    data["ollama_host"] = raw["ollama_host"].strip()
    except Exception:
        pass
    return data


def save_settings(gemini_api_key: str | None = None, scorer: str | None = None,
                  provider: str | None = None, deepseek_api_key: str | None = None,
                  ollama_model: str | None = None, ollama_host: str | None = None) -> dict:
    """Merge the given values into the settings file and return the new state.

    gemini_api_key="" clears the saved key (same for deepseek_api_key).
    scorer must be in SCORERS, provider in PROVIDERS.
    """
    data = load_settings()
    if gemini_api_key is not None:
        data["gemini_api_key"] = gemini_api_key.strip()
    if deepseek_api_key is not None:
        data["deepseek_api_key"] = deepseek_api_key.strip()
    if scorer is not None:
        if scorer not in SCORERS:
            raise ValueError(f"unknown scorer: {scorer}")
        data["scorer"] = scorer
    if provider is not None:
        if provider not in PROVIDERS:
            raise ValueError(f"unknown provider: {provider}")
        data["provider"] = provider
    if ollama_model is not None and ollama_model.strip():
        data["ollama_model"] = ollama_model.strip()
    if ollama_host is not None and ollama_host.strip():
        data["ollama_host"] = ollama_host.strip()
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(SETTINGS_PATH, 0o600)
    except Exception:
        pass
    return data


def get_gemini_key() -> str:
    """The active Gemini key: saved settings first, then the env var."""
    saved = load_settings().get("gemini_api_key", "")
    if saved:
        return saved
    return os.environ.get("GEMINI_API_KEY", "").strip()


def get_deepseek_key() -> str:
    """The active DeepSeek key: saved settings first, then the env var."""
    saved = load_settings().get("deepseek_api_key", "")
    if saved:
        return saved
    return os.environ.get("DEEPSEEK_API_KEY", "").strip()


def get_ollama_model() -> str:
    """The Ollama model name from settings (default qwen2.5:3b)."""
    return load_settings().get("ollama_model", "qwen2.5:3b")


def get_ollama_host() -> str:
    """The Ollama server URL from settings (default localhost:11434)."""
    return load_settings().get("ollama_host", "http://localhost:11434")


def key_source() -> str:
    """Where the active key comes from: 'settings', 'environment', or 'none'."""
    if load_settings().get("gemini_api_key"):
        return "settings"
    if os.environ.get("GEMINI_API_KEY", "").strip():
        return "environment"
    return "none"


def deepseek_key_source() -> str:
    """Where the active DeepSeek key comes from."""
    if load_settings().get("deepseek_api_key"):
        return "settings"
    if os.environ.get("DEEPSEEK_API_KEY", "").strip():
        return "environment"
    return "none"


def mask_key(key: str) -> str:
    """Masked form for display: first 4 + ... + last 4 characters."""
    if not key:
        return ""
    if len(key) <= 10:
        return key[:2] + "..." + key[-2:]
    return key[:4] + "..." + key[-4:]


def public_status() -> dict:
    """Safe-to-show status: never contains any key itself."""
    key = get_gemini_key()
    dkey = get_deepseek_key()
    return {
        "provider": load_settings().get("provider", "gemini"),
        "providers": list(PROVIDERS),
        "gemini_key_set": bool(key),
        "gemini_key_masked": mask_key(key),
        "gemini_key_source": key_source(),
        "deepseek_key_set": bool(dkey),
        "deepseek_key_masked": mask_key(dkey),
        "deepseek_key_source": deepseek_key_source(),
        "ollama_model": get_ollama_model(),
        "ollama_host": get_ollama_host(),
        "scorer": load_settings().get("scorer", "auto"),
        "scorers": list(SCORERS),
    }
