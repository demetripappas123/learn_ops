"""Azure AI Search retrieval — the real swap for the local Foundry IQ stand-in.

When USE_FOUNDRY_IQ=true and an Azure AI Search endpoint is configured,
``retrieve`` queries Azure AI Search. ANY failure returns ``None`` so callers
fall back to local Markdown retrieval. Azure packages are imported lazily, so
the core app runs with zero Azure dependencies installed.
"""
from __future__ import annotations

from certforge import config


def search_available() -> bool:
    """True only when Foundry IQ is enabled and an endpoint is configured."""
    return bool(config.use_foundry_iq() and config.search_endpoint())


def retrieve(query: str, top_k: int = 3) -> list[dict] | None:
    """Query Azure AI Search.

    Returns a list of ``{source, title, snippet, score}`` dicts (matching the
    local retrieval tool's shape), or ``None`` on any failure so the caller can
    fall back to local retrieval.
    """
    if not search_available():
        return None
    if not query or not query.strip():
        return []
    try:
        from azure.search.documents import SearchClient

        client = SearchClient(
            endpoint=config.search_endpoint(),
            index_name=config.search_index(),
            credential=_credential(),
        )
        results = client.search(
            search_text=query,
            top=top_k,
            select=["id", "title", "source", "content"],
        )
        hits: list[dict] = []
        for r in results:
            content = r.get("content") or ""
            hits.append(
                {
                    "source": r.get("source") or r.get("id") or config.search_index(),
                    "title": r.get("title") or "",
                    "snippet": content[:300],
                    "score": float(r.get("@search.score", 0.0)),
                }
            )
        return hits
    except Exception:
        # Fail safe: never let a search outage or misconfig break the demo.
        return None


def _credential():
    """Key auth if a key is present; otherwise keyless DefaultAzureCredential."""
    key = config.search_api_key()
    if key:
        from azure.core.credentials import AzureKeyCredential

        return AzureKeyCredential(key)
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential()
