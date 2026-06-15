"""Local knowledge retrieval tool — keyword scoring over certforge/knowledge/*.md."""

from __future__ import annotations

import re
from pathlib import Path

_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


def retrieve_knowledge(query: str, top_k: int = 3) -> list[dict]:
    """Score knowledge docs by query token overlap and return top_k results.

    Args:
        query: Free-text query string.
        top_k: Maximum number of results to return.

    Returns:
        List of dicts with keys: source, title, snippet, score.
        Returns [] if the knowledge folder is empty or missing.
    """
    if not query or not query.strip():
        return []

    # Foundry IQ (Azure AI Search) grounding when configured; falls back to local Markdown.
    from certforge.foundry import search_client
    if search_client.search_available():
        hits = search_client.retrieve(query, top_k)
        if hits is not None:
            return hits

    if not _KNOWLEDGE_DIR.exists():
        return []

    md_files = list(_KNOWLEDGE_DIR.glob("*.md"))
    if not md_files:
        return []

    tokens = set(re.split(r"[^a-z0-9]+", query.lower())) - {""}
    if not tokens:
        return []

    results: list[dict] = []
    for path in md_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue

        text_lower = text.lower()
        score = sum(1 for t in tokens if t in text_lower)

        # Derive title from first H1 or fall back to filename stem.
        title = path.stem
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                break

        # Find ~300-char snippet centred on the first query token match.
        snippet = text[:300]
        for token in tokens:
            idx = text_lower.find(token)
            if idx != -1:
                start = max(0, idx - 100)
                end = min(len(text), start + 300)
                snippet = text[start:end]
                break

        results.append(
            {
                "source": path.name,
                "title": title,
                "snippet": snippet,
                "score": score,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]
