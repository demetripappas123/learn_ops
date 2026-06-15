# CertForge Studio — Architecture

## Agent pipeline (deterministic orchestrator)

```
user request
     │
     ▼
Orchestrator ── loads synthetic LearnerProfile + WorkloadSignal
     │
     ├─▶ Project Intake Agent        → ProjectDefinition (stack, certs, difficulty)
     ├─▶ Learning Curator Agent      → LearningPath        [Retrieval Tool + Certification Mapper]
     ├─▶ Project Planner Agent       → TaskTree            [Task Tree Generator]
     ├─▶ Builder Coach Agent         → BuilderWorkflow     [Retrieval Tool (+ optional LLM enrich)]
     ├─▶ Assessment Agent            → AssessmentResult    [Readiness Scorer]
     ├─▶ Manager Insights Agent      → ManagerDashboard
     └─▶ Verifier Agent              → validated CertForgeResult
     │
     ▼
Telemetry Logger (JSONL traces)  →  CertForgeResult  →  Streamlit UI / CLI
```

The orchestrator is a plain, typed Python pipeline (Pydantic v2 models). "Agents" are
modules with pure-ish functions — easy to test, trace, and later wrap in Microsoft
Agent Framework.

## Retrieval: local ⇄ Foundry IQ (one swap point)

```
retrieve_knowledge(query)
     │
     ├─ USE_FOUNDRY_IQ=true  → Azure AI Search  (foundry/search_client.py)  ── the Foundry IQ grounding
     │        │ (any failure)
     │        └────────────┐
     ▼                     ▼
   local Markdown keyword scoring over certforge/knowledge/*.md   (always-available fallback)
```

All Azure access is **lazy-imported and fail-safe**: the core app needs zero Azure
packages, and any outage/misconfig silently falls back to local retrieval.

## Local (MVP) vs Azure (deployed)

| Concern | Local default | Azure deployment |
| --- | --- | --- |
| Retrieval / grounding | local Markdown keyword search | **Azure AI Search** (Foundry IQ) |
| Agent reasoning | deterministic Python | deterministic (+ optional **Azure OpenAI** enrichment) |
| Knowledge store | `certforge/knowledge/*.md` | Search index `certforge-knowledge` |
| Hosting | `streamlit run app.py` | **Azure Container Apps** (port 8501) |
| Identity / auth | none | **managed identity** (keyless) + RBAC |
| Telemetry | JSONL on disk | JSONL in container (maps to Foundry observability) |

## Azure topology (deployed)

```
            ┌──────────────────────────── Azure Container Apps ───────────────────────────┐
 Browser ──▶│  CertForge (Streamlit, non-root, system-assigned managed identity)          │
            └───────┬───────────────────────────────────────────────┬─────────────────────┘
                    │ Search Index Data Reader (RBAC, keyless)        │ Cognitive Services OpenAI User (optional)
                    ▼                                                 ▼
        ┌────────────────────────┐                       ┌────────────────────────────┐
        │  Azure AI Search        │  ◀── index_knowledge  │  Azure OpenAI (Foundry)     │
        │  index: certforge-      │       .py loads docs  │  deployment: gpt-4o         │
        │  knowledge (= Foundry IQ│                       │  (optional LLM enrichment)  │
        │  foundation)            │                       └────────────────────────────┘
        └────────────────────────┘
              ▲ image pull (AcrPull)
        ┌────────────────────────┐
        │  Azure Container Registry (certforge:latest, built via az acr build) │
        └────────────────────────┘
```

See `docs/AZURE_HANDOVER.md` for the exact provisioning commands.

## Microsoft IQ mapping

- **Foundry IQ** → Azure AI Search agentic-retrieval knowledge base (our index is the foundation).
- **Work IQ** → simulated by synthetic `workload_signals.json` (focus hours, meeting load, risk).
- **Fabric IQ** → simulated by structured `certification_matrix.json` / `skill_taxonomy.json` semantic data.
- No real user data is used.
