"""Central configuration for optional Azure / Foundry integration.

Local default (no env set): everything is OFF and the app runs fully offline and
deterministic. Populate a `.env` file (copy from `.env.example`) to switch on:

  * USE_FOUNDRY_IQ  -> Azure AI Search retrieval (the real Foundry IQ grounding)
  * USE_FOUNDRY_LLM -> Azure OpenAI (Foundry Models) concept enrichment

Both API-key and keyless (Microsoft Entra / managed identity) auth are supported.
If an API key is present it is used; otherwise DefaultAzureCredential is used.
"""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dotenv is a core dependency; stay defensive
    load_dotenv = None

_loaded = False


def load_env() -> None:
    """Load variables from a local `.env` file once (idempotent, best-effort).

    `override=False` means real environment variables (e.g. those injected by
    Azure Container Apps) always win over a checked-out `.env`.
    """
    global _loaded
    if _loaded:
        return
    if load_dotenv is not None:
        try:
            load_dotenv(override=False)
        except Exception:
            pass
    _loaded = True


def _bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


# --- Azure AI Search (Foundry IQ grounding) ------------------------------------
def use_foundry_iq() -> bool:
    return _bool("USE_FOUNDRY_IQ")


def search_endpoint() -> str | None:
    return os.getenv("AZURE_SEARCH_ENDPOINT") or None


def search_index() -> str:
    return os.getenv("AZURE_SEARCH_INDEX_NAME", "certforge-knowledge")


def search_api_key() -> str | None:
    return os.getenv("AZURE_SEARCH_API_KEY") or None


# --- Azure OpenAI in Foundry Models (optional LLM) -----------------------------
def use_foundry_llm() -> bool:
    return _bool("USE_FOUNDRY_LLM")


def openai_endpoint() -> str | None:
    return os.getenv("AZURE_OPENAI_ENDPOINT") or None


def openai_deployment() -> str:
    return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")


def openai_api_key() -> str | None:
    return os.getenv("AZURE_OPENAI_API_KEY") or None


def openai_api_version() -> str:
    return os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


# Load .env eagerly so importing this module is enough to populate config.
load_env()
