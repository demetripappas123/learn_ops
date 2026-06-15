"""Project Intake Agent: classifies a user request into a ProjectDefinition."""
from __future__ import annotations

import json
import re
from pathlib import Path

from certforge.schemas.models import ProjectDefinition

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_TAXONOMY_PATH = _DATA_DIR / "skill_taxonomy.json"

# DETERMINISM TABLE
_DOCUMENT_KEYWORDS = {
    "document", "forms", "pdf", "ocr", "extraction", "invoice", "scan",
}
_RAG_KEYWORDS = {
    "rag", "retrieval", "support assistant", "knowledge", "chatbot",
}
_SERVERLESS_KEYWORDS = {
    "serverless", "api", "functions", "endpoint", "microservice",
}


def _matches_any(request_lower: str, keywords: set[str]) -> bool:
    return any(kw in request_lower for kw in keywords)


def analyze_project_request(user_request: str) -> ProjectDefinition:
    """Classify user_request into a ProjectDefinition using the determinism table."""
    if not user_request or not str(user_request).strip():
        raise ValueError("user_request must be a non-empty string describing the project idea.")
    req = str(user_request).lower()

    if _matches_any(req, _DOCUMENT_KEYWORDS):
        taxonomy = _load_taxonomy()
        assumptions = _doc_assumptions(taxonomy)
        return ProjectDefinition(
            project_name="AI-Powered Document Processing Platform",
            user_request=user_request,
            project_category="Document Processing / AI Automation",
            detected_stack=[
                "Azure AI Foundry",
                "Azure AI Document Intelligence",
                "Azure Blob Storage",
                "Azure Functions",
                "Azure AI Search",
                "Microsoft Entra ID",
            ],
            target_certifications=["AI-102", "AZ-204"],
            difficulty="Intermediate",
            assumptions=assumptions,
        )

    if _matches_any(req, _RAG_KEYWORDS):
        return ProjectDefinition(
            project_name="RAG Support Assistant",
            user_request=user_request,
            project_category="RAG Knowledge Assistant",
            detected_stack=[
                "Azure AI Foundry",
                "Azure AI Search",
                "Azure OpenAI",
                "Azure Functions",
                "Azure Blob Storage",
                "Microsoft Entra ID",
            ],
            target_certifications=["AI-102", "AZ-204"],
            difficulty="Intermediate",
            assumptions=[
                "The knowledge base will be populated from existing documentation sources.",
                "Azure OpenAI will be used for embedding generation and answer synthesis.",
                "Authentication will use managed identity via Microsoft Entra ID.",
            ],
        )

    if _matches_any(req, _SERVERLESS_KEYWORDS):
        return ProjectDefinition(
            project_name="Serverless API Platform",
            user_request=user_request,
            project_category="Serverless API Platform",
            detected_stack=[
                "Azure Functions",
                "Azure API Management",
                "Azure Blob Storage",
                "Azure Monitor",
                "Microsoft Entra ID",
            ],
            target_certifications=["AZ-204"],
            difficulty="Intermediate",
            assumptions=[
                "APIs will be exposed via Azure API Management for rate limiting and security.",
                "Azure Functions will use a consumption plan for cost efficiency.",
                "Managed identity will be used to access downstream Azure services securely.",
            ],
        )

    # Default: document processing (case 4 → case 1)
    taxonomy = _load_taxonomy()
    assumptions = _doc_assumptions(taxonomy)
    return ProjectDefinition(
        project_name="AI-Powered Document Processing Platform",
        user_request=user_request,
        project_category="Document Processing / AI Automation",
        detected_stack=[
            "Azure AI Foundry",
            "Azure AI Document Intelligence",
            "Azure Blob Storage",
            "Azure Functions",
            "Azure AI Search",
            "Microsoft Entra ID",
        ],
        target_certifications=["AI-102", "AZ-204"],
        difficulty="Intermediate",
        assumptions=assumptions,
    )


def _load_taxonomy() -> dict:
    try:
        return json.loads(_TAXONOMY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _doc_assumptions(taxonomy: dict) -> list[str]:
    """Return 2-3 sensible assumptions for the document processing case."""
    risk_areas: list[str] = []
    try:
        risk_areas = taxonomy["document_processing_platform"]["risk_areas"]
    except (KeyError, TypeError):
        pass

    assumptions = [
        "Documents will be uploaded to Azure Blob Storage as the ingestion entry point.",
        "Azure AI Document Intelligence will handle structured extraction from PDFs and forms.",
        "Secure access to all services will be enforced via Microsoft Entra ID managed identity.",
    ]
    return assumptions
