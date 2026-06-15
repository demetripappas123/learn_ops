# CertForge Studio

## One-Line Pitch
Turn real project goals into certification-aligned learning workflows with multi-agent reasoning and IDE-integrated guidance.

## Demo Narrative

**Scenario:** A manager asks CertForge to upskill a team member on Azure cloud architecture while building a production data pipeline.

1. **Project Intake** → CertForge analyzes the project requirements and learning goals.
2. **Certification Mapping** → The system identifies which Microsoft role-based certifications align (e.g., Azure Data Engineer Associate, Azure Solutions Architect).
3. **Task Tree Generation** → A structured breakdown of implementation milestones emerges, each tagged with required skills.
4. **IDE Guidance** → As the learner codes, context-aware prompts appear with architectural best practices and skill reinforcement.
5. **Mastery Assessment** → Grounded questions validate understanding at decision points (not just "what" but "why").
6. **Manager Visibility** → A readiness dashboard shows skill gaps, risk vectors, and certification progress in real time.
7. **Certification Proof** → On completion, CertForge generates a claim of competency backed by demonstrated work.

---

## Why This Matters

Enterprise learning is broken. Companies silo training from work:
- **Training is detached.** Online courses don't teach *your* system.
- **Learning is passive.** Developers memorize facts instead of building judgment.
- **Readiness is opaque.** Managers don't know who can own critical projects until it's too late.
- **Certification is hollow.** Certs don't prove you can do the work.

**CertForge fixes this.** By weaving certification requirements into real project work, we align learning with business value, build judgment through authentic practice, and give managers early warning of skill gaps—all without extra training overhead.

---

## Challenge Alignment: Microsoft Reasoning Agents – Challenge A: Enterprise Learning System

CertForge Studio directly addresses the challenge brief:

| Challenge Requirement | CertForge Solution |
|---|---|
| **Reasoning agents for learning workflows** | 7-agent multi-agent system orchestrates project analysis, certification mapping, task generation, guidance, assessment, and visibility. |
| **Integration with Microsoft tech stack** | Built on Azure AI (OpenAI GPT models), Foundry Agent Framework, and Hosted Agents for enterprise deployment. |
| **Certification-aligned skill building** | Maps projects to Microsoft role-based certifications (Azure roles, modern work skills). |
| **IDE/workflow integration** | Generates context-aware prompts and guidance at development time via Streamlit and agent APIs. |
| **Measurable competency** | Grounds assessment in demonstrated work artifacts and grounded multiple-choice questions. |
| **Manager visibility** | Real-time dashboard of skill gaps, risk flags, and certification progress. |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Manager / Learner Portal                    │
│                    (Streamlit + React Frontend)                  │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
    ┌────────▼────────────┐         ┌─────────────▼────────────┐
    │  Project Intake UI  │         │  Readiness Dashboard    │
    │  (Goals, Stack)     │         │  (Skills, Gaps, Risk)   │
    └────────┬────────────┘         └─────────────▲────────────┘
             │                                    │
      ┌──────▼──────────────────────────────────┬┴──────────────┐
      │                                          │               │
      │        ┌──────────────────────────────────────────────┐  │
      │        │        Multi-Agent Orchestration             │  │
      │        │  (Python + Anthropic / Azure OpenAI SDK)    │  │
      │        └──────────────────────────────────────────────┘  │
      │              │           │           │           │       │
      │    ┌─────────┴─┐  ┌──────┴──┐  ┌────┴────┐  ┌──┴────┐  │
      │    │ Project   │  │Learning │  │Task     │  │Guidance│  │
      │    │Analyzer   │  │Curator  │  │Planner  │  │Agent   │  │
      │    │Agent      │  │Agent    │  │Agent    │  │        │  │
      │    └─────┬─────┘  └────┬────┘  └────┬────┘  └──┬─────┘  │
      │          │             │            │          │         │
      │    ┌─────┴──────┐  ┌───┴────┐  ┌────┴────┐  ┌─┴──────┐  │
      │    │Assessment │  │Readiness│  │Telemetry│  │Cert    │  │
      │    │Agent      │  │Agent    │  │Agent    │  │Generator│  │
      │    └─────┬──────┘  └───┬────┘  └────┬────┘  └────────┘  │
      │          │             │            │                   │
      └──────────┼─────────────┼────────────┼───────────────────┘
                 │             │            │
      ┌──────────┴─────────────┴────────────┴──────────────────┐
      │           Knowledge & State Layer                       │
      ├──────────────────────────────────────────────────────────┤
      │  • Markdown Certification Specs (MVP for Foundry IQ)   │
      │  • Synthetic Workload Signals (MVP for Work IQ)        │
      │  • Skill Graph & Task Tree (MVP for Fabric IQ)         │
      │  • Assessment Results & Claims Database                │
      └──────────────────────────────────────────────────────────┘
```

---

## Agent Responsibilities

### 1. **Project Intake Agent**
Classifies the user's project idea, detects the Azure stack, infers target certifications and difficulty, and states explicit assumptions.  
*Output:* `ProjectDefinition` (stack, target certifications, difficulty, assumptions).

### 2. **Learning Curator Agent**
Maps the target certifications to their skill objectives (AI-102 / AZ-204), compares them against the learner's known skills to find gaps, and grounds recommendations in the local knowledge base (Foundry IQ stand-in).  
*Output:* `LearningPath` (required skills, missing skills, certification objectives, grounded snippets).

### 3. **Project Planner Agent**
Decomposes the project into milestones and a dependency-aware task tree with learning and assessment checkpoints on each task.  
*Output:* `TaskTree` (milestones + tasks with dependencies and certification mapping).

### 4. **Builder Coach Agent**
Generates IDE-level implementation guidance for a selected task: step-by-step plan, a Copilot prompt, a grounded concept explanation, a validation checklist, and common mistakes.  
*Output:* `BuilderWorkflow` (the "learning embedded in execution" differentiator).

### 5. **Assessment Agent**
Generates **original, project-specific** grounded questions mapped to certification objectives (never real exam items), with expected answers, explanations, and source references, then computes a readiness score.  
*Output:* `AssessmentResult` (questions, readiness score/level, weak areas, next actions).

### 6. **Manager Insights Agent**
Aggregates project progress, certification coverage, and conceptual risk areas into a manager-facing dashboard with recommendations.  
*Output:* `ManagerDashboard` (progress %, AZ-204/AI-102 coverage, risk areas).

### 7. **Verifier Agent**
Validates that every section is present and demo-critical, confirms questions are project-grounded (not exam dumps) and that citations and risk areas exist, and fills safe defaults.  
*Output:* A verified `CertForgeResult` plus a verification trace step.

**Supporting tools:** Retrieval Tool (local Foundry IQ stand-in), Certification Mapper, Task Tree Generator, Readiness Scorer, and the JSONL Telemetry Logger — surfaced in the agent trace.

---

## Microsoft IQ Strategy

CertForge Studio is architected to evolve as Microsoft Foundry IQ matures:

### **Current State (MVP)**
- **Local Markdown retrieval** stands in for Foundry IQ semantic search. Certification specs and skill hierarchies are stored as versioned Markdown files.
- **Synthetic workload signals** simulate Work IQ context (e.g., mock deployment logs, synthetic error traces, simulated project metrics).
- **Hardcoded skill graph** simulates Fabric IQ reasoning (e.g., structured certification → skill mappings).
- **No real user data.** All telemetry is synthetic or anonymized.

### **Roadmap to Foundry IQ Integration**
1. **Learning Curator & Assessment Agents** will query live Foundry IQ semantic index for role definitions, certification updates, and industry skill benchmarks.
2. **Telemetry Agent** will ingest Work IQ signals (real project telemetry, deployment outcomes, error patterns) to ground readiness assessments.
3. **Task Planner** will leverage Fabric IQ to refine task recommendations based on broader semantic context.
4. **Manager visibility** will pull from Foundry dashboards for company-wide skill benchmarking and risk trending.

### **Why This Approach**
- **Decouples agent logic from IQ service maturity.** Works today; scales when Foundry is ready.
- **Grounds all agents in reasoning.** MVPs are real implementations, not stubs.
- **Enables responsible AI.** Synthetic data prevents unintended leakage while we validate the learning model.

---

## Synthetic Data Notice

**CertForge Studio uses synthetic or anonymized data exclusively in this demo:**
- Project definitions are anonymized templates (no real customer projects).
- Workload signals are simulated (mock deployment logs, synthetic errors, synthetic project metrics).
- Assessment responses are generated or anonymized.
- No real employee skill histories or personal data are stored.

**This protects privacy while we validate the learning reasoning model.** In production, enterprises own and control their data, with explicit consent and data governance policies.

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/certforge/certforge-studio.git
cd certforge-studio

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) configure Azure — copy the template and fill in values.
# Leave it untouched to run the fully local, deterministic demo.
cp .env.example .env
# See .env.example for the Azure AI Search (Foundry IQ) and Azure OpenAI settings.

# Run the main agent orchestrator (with logging)
python main.py

# In a new terminal (with .venv activated), start the Streamlit UI
streamlit run app.py

# (Optional) Run evaluation suite
python -m certforge.evals.run_evals
```

The Streamlit app will be available at `http://localhost:8501`.

---

## Azure Deployment & Foundry Integration

CertForge runs **fully local and deterministic by default**. Two optional flags switch on real Azure services. All Azure calls are lazy-imported and fail-safe — a misconfiguration falls back to local retrieval, so the demo never breaks.

| Flag | Turns on | Service |
| --- | --- | --- |
| `USE_FOUNDRY_IQ=true` | retrieval grounding | **Azure AI Search** (the Foundry IQ foundation) |
| `USE_FOUNDRY_LLM=true` | concept enrichment | **Azure OpenAI** in Foundry Models (`gpt-4o`) |

```bash
# Install the optional Azure extras only when using Azure:
pip install -r requirements-azure.txt
# Load the knowledge docs into Azure AI Search (one-time):
python scripts/index_knowledge.py
```

- **Full provisioning + deploy guide:** [`docs/AZURE_HANDOVER.md`](docs/AZURE_HANDOVER.md) — copy-paste `az` CLI for Azure AI Search, Azure OpenAI, and **Azure Container Apps** (managed identity, RBAC, `az acr build` — no local Docker needed).
- **Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- **Config template:** [`.env.example`](.env.example) — supports both API-key and keyless (managed identity) auth.

---

## Demo Flow

1. **Project Intake** (UI)
   - Enter project title, description, tech stack, duration, team size.
   - CertForge ingests and stores the project profile.

2. **Agent Orchestration** (Backend)
   - Project Analyzer extracts skills and risks.
   - Learning Curator maps to Microsoft certifications.
   - Task Planner builds a task tree.
   - Guidance Agent pre-generates context snippets.

3. **Interactive Dashboard** (UI)
   - View certification roadmap with milestone checkpoints.
   - See real-time readiness scores (skill gaps, risk flags).
   - Access in-context guidance and assessment questions.

4. **Assessment Loop** (Backend)
   - Assessment Agent evaluates learner responses and code artifacts.
   - Signals are logged to telemetry.
   - Dashboard updates readiness and risk in real time.

5. **Certification Proof** (UI)
   - On project completion, view a competency claim signed by CertForge.
   - Download a structured certification proof for portfolio / resume.

---

## Evaluation and Telemetry

### **Agent Reasoning Traces**
- Each agent logs its reasoning chain, supporting facts, and confidence scores.
- Traces are persisted in structured JSON for audit and improvement.

### **Skill Assessment Accuracy**
- Ground-truth: learner's actual work artifacts and peer reviews.
- CertForge assessments are compared against ground truth.
- Precision, recall, and F1 metrics tracked per certification track.

### **Readiness Prediction**
- Does CertForge's readiness score correlate with actual project success?
- Tracked via post-project manager feedback and objective KPIs (deployment success, incident rates, code review feedback).

### **Learning Effectiveness**
- Pre/post skill self-assessments.
- Time to competency (certification path completion time).
- Engagement metrics (UI interactions, guidance adoption, assessment attempt rate).

### **Telemetry Collection**
- Structured event logging (agent decisions, assessment responses, UI interactions).
- Anonymized trace collection for continuous model improvement.
- No PII unless explicitly consented by enterprise administrators.

---

## Security and Responsible AI

### **Data Privacy**
- All data encrypted in transit (TLS) and at rest.
- No user data persists beyond the project lifecycle unless explicitly retained.
- GDPR/HIPAA-compliant data handling for enterprise deployments.

### **Model Governance**
- Agent decisions are explainable; reasoning traces are logged and auditable.
- Assessments are grounded in work artifacts, not opaque heuristics.
- Certification claims are signed and timestamped for integrity.

### **Bias & Fairness**
- Synthetic data prevents training bias from real historical data.
- Certification mappings are reviewed by domain experts (Microsoft Learning partners) quarterly.
- Readiness assessments account for diverse learning styles and prior experience.

### **Responsible Scaling**
- Agents respect rate limits and cost caps; telemetry is sampled when needed.
- Enterprise deployments include data residency and compliance controls.
- No model fine-tuning without explicit audit and approval.

---

## Future Foundry Deployment Story

As Microsoft Foundry matures, CertForge evolves:

### **Phase 1: Foundry Agent Framework**
- Migrate orchestration from local Python to Foundry Agent Framework.
- Agents become Foundry-managed services with lifecycle management, versioning, and rollback.

### **Phase 2: Foundry IQ Integration**
- **Learning Curator** queries live Foundry IQ semantic index for role definitions.
- **Assessment Agent** grounds competency checks in Foundry skill graphs.
- **Task Planner** leverages Fabric IQ reasoning for task optimization.

### **Phase 3: Hosted Agents in Foundry Agent Service**
- Deploy agents on Foundry's managed infrastructure.
- Automatic identity/auth, observability, audit, and compliance integration.
- Hosted agents eliminate local DevOps burden and ensure enterprise SLAs.

### **Phase 4: Multi-Tenant Enterprise Platform**
- Foundry multi-tenancy isolates customer data and configurations.
- Real Work IQ signals (actual project telemetry) integrate with assessment.
- Manager dashboards pull from Foundry observability for company-wide skill trending.

### **Telemetry & Observability Roadmap**
- Current: Structured JSON logs from local agents.
- Future: Traces map to Foundry observability (Application Insights, OpenTelemetry, Copilot analytics).
- Result: Unified view of learning outcomes, agent reasoning, and business impact across enterprises.

---

## CertForge Studio is a project-based enterprise learning agent system built for the Microsoft Reasoning Agents challenge. Instead of separating training from work, CertForge turns real project goals into certification-aligned learning workflows. A multi-agent system analyzes the requested project, maps it to Microsoft role-based certifications, creates a task tree, generates IDE-level implementation guidance, assesses mastery through grounded questions, and gives managers visibility into readiness and risk. Microsoft IQ Strategy section must explain: local Markdown retrieval is the MVP stand-in for Foundry IQ; Foundry IQ would ground the Learning Curator and Assessment Agent; synthetic workload signals simulate Work IQ context; structured skill/certification data simulates Fabric IQ semantic reasoning; no real user data. Future Foundry section: migrate orchestration into Microsoft Agent Framework; Foundry IQ replaces local retrieval; Hosted Agents in Foundry Agent Service for managed deployment/identity/observability; telemetry traces map to Foundry observability.

---

## Built With

- **Claude Code & GitHub Copilot** – Multi-agent system design, agent implementation, and reasoning trace generation.
- **Anthropic Claude API** – Primary reasoning backbone for agent orchestration.
- **Azure OpenAI & Semantic Kernel** – Secondary model support and embeddings.
- **Streamlit** – Interactive UI for project intake, dashboards, and assessment.
- **Python 3.10+** – Core language; async patterns for agent coordination.
- **Pydantic** – Type-safe configuration and data validation.
- **SQLite / PostgreSQL** – Project and assessment data persistence.
- **OpenTelemetry** – Structured telemetry and observability instrumentation.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

Licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Contact & Support

- **Email:** support@certforge.ai
- **Issues:** [GitHub Issues](https://github.com/certforge/certforge-studio/issues)
- **Documentation:** [CertForge Docs](https://docs.certforge.ai)

---

**Built for the future of enterprise learning. One project. One agent system. One certification at a time.**
