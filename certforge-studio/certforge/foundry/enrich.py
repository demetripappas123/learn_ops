"""Optional LLM enrichment hooks (behind USE_FOUNDRY_LLM). All fall back safely.

Note: enrichment is deliberately limited to EXPLANATORY content (concept
explanations). Assessment questions stay deterministic and locally authored so
the "no real exam questions" guarantee is never delegated to a model.
"""
from __future__ import annotations

from certforge.foundry.llm_client import complete, llm_available


def enrich_concept(task_title: str, skills: list[str], base_explanation: str) -> str:
    """Return an LLM-expanded concept explanation, or the deterministic base on failure."""
    if not llm_available():
        return base_explanation
    system = (
        "You are a Microsoft Azure certification coach. Expand the learner's "
        "concept explanation. Be accurate, concise (max ~120 words), grounded in "
        "Azure best practices, and do not invent product names."
    )
    user = (
        f"Task: {task_title}\n"
        f"Related skills: {', '.join(skills) if skills else 'n/a'}\n"
        f"Current explanation: {base_explanation}\n\n"
        "Return an improved explanation only."
    )
    out = complete(system, user, max_tokens=300, temperature=0.3)
    return out or base_explanation
