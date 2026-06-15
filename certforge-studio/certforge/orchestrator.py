"""
orchestrator.py — deterministic pipeline that ties all CertForge agents together.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from certforge.schemas.models import (
    AgentTraceStep,
    CertForgeResult,
    LearnerProfile,
    WorkloadSignal,
)
from certforge.agents.project_intake_agent import analyze_project_request
from certforge.agents.learning_curator_agent import curate_learning_path
from certforge.agents.project_planner_agent import generate_project_task_tree
from certforge.agents.builder_coach_agent import generate_builder_workflow
from certforge.agents.assessment_agent import generate_assessment
from certforge.agents.manager_insights_agent import generate_manager_dashboard
from certforge.agents.verifier_agent import verify_result
from certforge.tools.telemetry_logger import log_trace

_DATA_DIR = Path(__file__).parent / "data"


def _load_learner(learner_id: str) -> LearnerProfile:
    """Load a learner by ID from learners.json; fall back to EMP-001."""
    learners_path = _DATA_DIR / "learners.json"
    learners = json.loads(learners_path.read_text())
    if not learners:
        raise RuntimeError("learners.json contains no learner records.")
    by_id = {l["learner_id"]: l for l in learners}
    record = by_id.get(learner_id) or by_id.get("EMP-001") or learners[0]
    return LearnerProfile(**record)


def _load_workload(learner_id: str) -> WorkloadSignal:
    """Load workload signal for a learner; fall back to EMP-001."""
    workload_path = _DATA_DIR / "workload_signals.json"
    signals = json.loads(workload_path.read_text())
    if not signals:
        raise RuntimeError("workload_signals.json contains no records.")
    by_id = {s["learner_id"]: s for s in signals}
    record = by_id.get(learner_id) or by_id.get("EMP-001") or signals[0]
    return WorkloadSignal(**record)


def run_certforge_flow(
    user_request: str,
    learner_id: str = "EMP-001",
    selected_task_id: str | None = None,
) -> CertForgeResult:
    """
    Execute the full CertForge pipeline deterministically.

    Pipeline order:
    Orchestrator -> Project Intake -> Learning Curator -> Project Planner
    -> Builder Coach -> Assessment -> Manager Insights -> Verifier
    """
    trace: list[AgentTraceStep] = []

    # ── Orchestrator bootstrap ──────────────────────────────────────────────
    trace.append(AgentTraceStep(
        agent_name="Orchestrator",
        action="Pipeline initialised",
        input_summary=f"user_request={user_request!r}, learner_id={learner_id!r}, selected_task_id={selected_task_id!r}",
        output_summary="Loaded learner profile and workload signal; starting agent chain.",
        tools_used=["learners.json", "workload_signals.json"],
    ))

    learner = _load_learner(learner_id)
    workload = _load_workload(learner_id)

    # ── Project Intake Agent ────────────────────────────────────────────────
    project = analyze_project_request(user_request)
    trace.append(AgentTraceStep(
        agent_name="Project Intake Agent",
        action="Classify user request and define project",
        input_summary=f"user_request={user_request!r}",
        output_summary=(
            f"project_name={project.project_name!r}, "
            f"category={project.project_category!r}, "
            f"stack={project.detected_stack}, "
            f"certs={project.target_certifications}"
        ),
        tools_used=["skill_taxonomy.json", "determinism_table"],
    ))

    # ── Learning Curator Agent ──────────────────────────────────────────────
    learning_path = curate_learning_path(project, learner)
    trace.append(AgentTraceStep(
        agent_name="Learning Curator Agent",
        action="Map certification objectives and identify skill gaps",
        input_summary=(
            f"project_certs={project.target_certifications}, "
            f"known_skills={learner.known_skills}"
        ),
        output_summary=(
            f"required_skills_count={len(learning_path.required_skills)}, "
            f"missing_skills={learning_path.missing_skills}, "
            f"resources_count={len(learning_path.recommended_resources)}"
        ),
        tools_used=["certification_mapper", "retrieve_knowledge", "certification_matrix.json"],
    ))

    # ── Project Planner Agent ───────────────────────────────────────────────
    task_tree = generate_project_task_tree(project, learning_path, workload)
    trace.append(AgentTraceStep(
        agent_name="Project Planner Agent",
        action="Generate milestone-based task tree",
        input_summary=(
            f"project_category={project.project_category!r}, "
            f"missing_skills_count={len(learning_path.missing_skills)}, "
            f"workload_risk={workload.workload_risk!r}"
        ),
        output_summary=(
            f"milestones={task_tree.milestones}, "
            f"task_count={len(task_tree.tasks)}"
        ),
        tools_used=["create_document_processing_task_tree", "create_generic_task_tree"],
    ))

    # ── Select task for deep dive ───────────────────────────────────────────
    if selected_task_id is not None:
        task = next(
            (t for t in task_tree.tasks if t.task_id == selected_task_id),
            task_tree.tasks[0],
        )
    else:
        task = task_tree.tasks[0]

    # ── Builder Coach Agent ─────────────────────────────────────────────────
    builder_workflow = generate_builder_workflow(task, project, learning_path)
    trace.append(AgentTraceStep(
        agent_name="Builder Coach Agent",
        action="Generate implementation workflow for selected task",
        input_summary=f"task_id={task.task_id!r}, task_title={task.title!r}",
        output_summary=(
            f"implementation_steps_count={len(builder_workflow.implementation_steps)}, "
            f"validation_checklist_count={len(builder_workflow.validation_checklist)}"
        ),
        tools_used=["retrieve_knowledge"],
    ))

    # ── Assessment Agent ────────────────────────────────────────────────────
    assessment = generate_assessment(task, learning_path, project)
    trace.append(AgentTraceStep(
        agent_name="Assessment Agent",
        action="Generate certification-aligned assessment questions",
        input_summary=f"task_id={task.task_id!r}, missing_skills={learning_path.missing_skills}",
        output_summary=(
            f"readiness_score={assessment.readiness_score}, "
            f"readiness_level={assessment.readiness_level!r}, "
            f"questions_count={len(assessment.questions)}, "
            f"weak_areas={assessment.weak_areas}"
        ),
        tools_used=["calculate_readiness_score"],
    ))

    # ── Manager Insights Agent ──────────────────────────────────────────────
    manager_dashboard = generate_manager_dashboard(project, task_tree, assessment)
    trace.append(AgentTraceStep(
        agent_name="Manager Insights Agent",
        action="Build manager dashboard with progress and risk signals",
        input_summary=(
            f"project_name={project.project_name!r}, "
            f"task_count={len(task_tree.tasks)}, "
            f"weak_areas={assessment.weak_areas}"
        ),
        output_summary=(
            f"progress={manager_dashboard.project_progress_percent}%, "
            f"az204={manager_dashboard.az204_coverage_percent}%, "
            f"ai102={manager_dashboard.ai102_coverage_percent}%, "
            f"risk_areas={manager_dashboard.risk_areas}"
        ),
        tools_used=["manager_progress.json"],
    ))

    # ── Assemble pre-verification result ───────────────────────────────────
    result = CertForgeResult(
        project=project,
        learner_profile=learner,
        workload=workload,
        learning_path=learning_path,
        task_tree=task_tree,
        builder_workflow=builder_workflow,
        assessment=assessment,
        manager_dashboard=manager_dashboard,
        trace=trace,
    )

    # ── Verifier Agent ──────────────────────────────────────────────────────
    result = verify_result(result)
    # Verifier appends its own AgentTraceStep internally; capture final trace.

    # ── Telemetry ───────────────────────────────────────────────────────────
    request_id = str(uuid.uuid4())
    log_trace(result.trace, request_id=request_id)

    return result
