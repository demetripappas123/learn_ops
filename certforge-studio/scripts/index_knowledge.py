"""Create the Azure AI Search index and upload CertForge knowledge docs.

This is the one-time (or refresh) step that gives the "Foundry IQ" grounding its
content. After this runs, set USE_FOUNDRY_IQ=true and the app retrieves from
Azure AI Search instead of local Markdown.

Usage (from the certforge-studio directory, with .env configured):
    pip install -r requirements-azure.txt
    python scripts/index_knowledge.py

Auth: uses AZURE_SEARCH_API_KEY if set (must be an ADMIN key to create/load),
otherwise DefaultAzureCredential (your `az login` identity, which needs the
"Search Service Contributor" + "Search Index Data Contributor" roles).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the `certforge` package importable when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from certforge import config  # noqa: E402

_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "certforge" / "knowledge"


def _credential():
    key = config.search_api_key()
    if key:
        from azure.core.credentials import AzureKeyCredential

        return AzureKeyCredential(key)
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential()


def _title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def build_index() -> None:
    endpoint = config.search_endpoint()
    if not endpoint:
        raise SystemExit("AZURE_SEARCH_ENDPOINT is not set. Configure your .env first.")
    index_name = config.search_index()

    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchableField,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
    )

    credential = _credential()

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
    ]
    index = SearchIndex(name=index_name, fields=fields)

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    index_client.create_or_update_index(index)
    print(f"Index '{index_name}' created/updated.")

    docs = []
    for i, path in enumerate(sorted(_KNOWLEDGE_DIR.glob("*.md"))):
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "id": f"doc-{i}-{path.stem}",
                "title": _title_of(text, path.stem),
                "source": path.name,
                "content": text,
            }
        )

    if not docs:
        print("No knowledge documents found to upload.")
        return

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    result = search_client.upload_documents(documents=docs)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(docs)} documents to index '{index_name}'.")


if __name__ == "__main__":
    build_index()
