# CertForge Studio Architecture

## System Overview

CertForge Studio is an AI-driven certification learning platform that orchestrates multiple specialized agents to guide users through personalized learning journeys toward industry certifications.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Request                                 │
│              (Certification goal, experience level, time)            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Orchestrator Agent                              │
│            (Routes requests to specialized agents)                   │
└──────────┬────────────┬──────────────┬────────────┬─────────────────┘
           │            │              │            │
    ┌──────▼──┐  ┌──────▼─────┐  ┌───▼─────┐  ┌──▼──────────┐
    │ Project │  │  Learning  │  │ Project │  │   Builder   │
    │ Intake  │  │  Curator   │  │ Planner │  │    Coach    │
    │ Agent   │  │  Agent     │  │ Agent   │  │    Agent    │
    └────┬────┘  └──────┬─────┘  └───┬─────┘  └──┬──────────┘
         │               │            │           │
         │         ┌─────▼─────┐     │           │
         │         │ Retrieval │     │           │
         │         │   Tool    │     │           │
         │         │(Foundry IQ│     │           │
         │         │ stand-in) │     │           │
         │         │ + Local   │     │           │
         │         │ Knowledge │     │           │
         │         │   Base    │     │           │
         │         └──────┬────┘     │           │
         │                │          │           │
         │         ┌──────▼──────┐   │           │
         │         │Certification│   │           │
         │         │   Mapper    │   │           │
         │         └──────┬──────┘   │           │
         │                │          │           │
    ┌────┴────────────────┴──────────┴───────────┴──────────┐
    │                                                        │
    ▼                          ▼                            ▼
┌──────────┐  ┌───────────────────┐  ┌──────────────────────┐
│Assessment│  │  Manager Insights │  │     Verifier Agent   │
│  Agent   │  │      Agent        │  │                      │
│(Readiness│  │                   │  │ (Validates learning  │
│ Scorer)  │  │                   │  │  milestones, tests)  │
└──────┬───┘  └─────────┬─────────┘  └──────────┬───────────┘
       │                 │                       │
       └─────────────────┴───────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │    Telemetry Logger Agent         │
         │  (Captures JSONL traces of all    │
         │   agent interactions, decisions,  │
         │   and learning progress)          │
         └────────────────┬──────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │      CertForgeResult Object       │
         │  (Aggregates outputs from all     │
         │   agents into unified response)   │
         └────────────────┬──────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │       Streamlit UI Display        │
         │  (Renders learning plan,          │
         │   progress tracking, insights,    │
         │   assessment results)             │
         └───────────────────────────────────┘
```

## Agent Components

### 1. **Orchestrator Agent**
- Entry point for all user requests
- Routes to appropriate specialized agents based on request type
- Coordinates multi-agent workflows
- Manages context and state across the pipeline

### 2. **Project Intake Agent**
- Collects user information (certification goal, experience level, availability)
- Validates certification requests against knowledge base
- Establishes baseline metrics and learning objectives
- Outputs: User profile and initial assessment

### 3. **Learning Curator Agent**
- Synthesizes learning resources and curriculum mapping
- Integrates with **Retrieval Tool** (Foundry IQ stand-in) to fetch relevant content
- Uses **Certification Mapper** to align resources with exam domains
- Leverages local knowledge base for domain expertise
- Outputs: Curated learning path with resource recommendations

### 4. **Project Planner Agent**
- Uses **Task Tree Generator** to decompose certification goal into milestones
- Creates hierarchical learning schedule
- Allocates time based on user availability and complexity
- Outputs: Detailed project plan with milestone definitions

### 5. **Builder Coach Agent**
- Provides personalized guidance and motivation
- Tracks learner progress against milestones
- Suggests pace adjustments and focus areas
- Outputs: Coaching recommendations and encouragement

### 6. **Assessment Agent (Readiness Scorer)**
- Evaluates learner readiness at key checkpoints
- Benchmarks progress against certification requirements
- Identifies knowledge gaps
- Outputs: Readiness scores and gap analysis

### 7. **Manager Insights Agent**
- Aggregates performance data across learning journey
- Provides high-level insights and trends
- Recommends optimization strategies
- Outputs: Analytics dashboard data and insights

### 8. **Verifier Agent**
- Validates learning milestones completion
- Simulates or integrates with mock certification tests
- Confirms readiness for actual certification exam
- Outputs: Verification results and final readiness assessment

### 9. **Telemetry Logger Agent**
- Captures all interactions, decisions, and outcomes
- Logs structured traces in JSONL format for debugging and analytics
- Preserves chain-of-thought for each agent
- Enables post-hoc analysis and continuous improvement

## Data Assets

### Synthetic Data
- Mock user profiles with varied experience levels
- Sample learning trajectories and completion rates
- Simulated exam scores and performance metrics
- Demo certification domains and exam blueprints

### Local Knowledge Base
- Foundational study materials for supported certifications
- Domain-specific learning resources and references
- Sample practice questions and assessments
- Certification mapping and prerequisite structures

## Result Aggregation

**CertForgeResult** object consolidates outputs from all agents:
- User profile and learning context
- Curated learning path and resources
- Project plan with timeline
- Progress metrics and readiness scores
- Manager insights and recommendations
- Verification status

## Frontend Display

**Streamlit UI** visualizes:
- Personalized learning roadmap
- Current progress and milestones
- Recommended next steps
- Readiness assessment results
- Performance analytics and insights
- Resource recommendations
- Mock exam practice interface

## Data Flow

1. **User Request** → Orchestrator
2. Orchestrator triggers parallel agents for intake, planning, and curation
3. Agents enrich request with data from local knowledge base and retrieval tool
4. All agent outputs logged to Telemetry Logger (JSONL traces)
5. Results aggregated into CertForgeResult object
6. Streamlit UI renders unified experience for learner

## Technology Considerations

- **Local-First**: Knowledge base and learning materials stored locally for privacy
- **Async Orchestration**: Agents run in parallel where possible for efficiency
- **Structured Logging**: JSONL traces enable observability and debugging
- **Mock Data**: Synthetic data ensures demo functionality without live dependencies
- **Modular Design**: Easy to swap real Foundry IQ integration for stand-in, or add real certification data sources
