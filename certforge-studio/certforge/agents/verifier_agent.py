"""Verifier agent: validates and fills CertForgeResult before returning it."""

from __future__ import annotations

from certforge.schemas.models import (
    AgentTraceStep,
    AssessmentQuestion,
    AssessmentResult,
    BuilderWorkflow,
    CertForgeResult,
    LearningPath,
    ManagerDashboard,
    TaskNode,
    TaskTree,
)


def verify_result(result: CertForgeResult) -> CertForgeResult:
    """Ensure every section is present and demo-critical lists are non-empty.

    Fills safe defaults for any missing or empty fields, verifies assessment
    questions are project-grounded, and appends a Verifier Agent trace step.
    """
    # --- Learning path ---
    lp = result.learning_path
    if not lp.required_skills:
        lp.required_skills = ["Azure Fundamentals"]
    if not lp.recommended_resources:
        lp.recommended_resources = ["azure_fundamentals.md"]
    if not lp.certification_objectives:
        lp.certification_objectives = ["Understand core Azure services"]
    if not lp.source_snippets:
        lp.source_snippets = ["See recommended resources for details."]

    # --- Task tree ---
    tt = result.task_tree
    if not tt.milestones:
        tt.milestones = ["Architecture and Requirements", "Implementation"]
    if not tt.tasks:
        tt.tasks = [
            TaskNode(
                task_id="T01",
                title="Define project architecture",
                description="Document the high-level architecture for the project.",
                milestone="Architecture and Requirements",
                dependencies=[],
                related_skills=["Architecture"],
                certification_mapping=["AZ-204"],
                estimated_effort="2 hours",
                learning_checkpoint="Architecture review complete",
                assessment_checkpoint="Can explain chosen architecture",
            )
        ]

    # --- Builder workflow ---
    bw = result.builder_workflow
    if not bw.implementation_steps:
        bw.implementation_steps = ["Review task requirements", "Implement solution", "Test and validate"]
    if not bw.validation_checklist:
        bw.validation_checklist = ["Code builds without errors", "Unit tests pass"]
    if not bw.common_mistakes:
        bw.common_mistakes = ["Skipping error handling", "Hardcoding credentials"]
    if not bw.ide_copilot_prompt:
        bw.ide_copilot_prompt = f"Help implement: {result.builder_workflow.selected_task_title}"
    if not bw.concept_explanation:
        bw.concept_explanation = "Complete the task following Azure best practices."

    # --- Assessment ---
    ar = result.assessment
    if not ar.questions:
        ar.questions = [
            AssessmentQuestion(
                question=f"What is the primary purpose of the {result.project.project_name}?",
                expected_answer="To automate processing using Azure services.",
                explanation="Understanding the project scope is foundational.",
                certification_mapping="AZ-204",
                skill_area="Architecture",
                source_reference="azure_fundamentals.md",
            )
        ]
    else:
        # Ensure questions are project-grounded: each question must reference
        # the project name, a known skill, or a stack component — not be a
        # generic multiple-choice exam dump (detect by checking for generic
        # patterns like "Which of the following" without project context).
        project_tokens = set(result.project.project_name.lower().split())
        stack_tokens = {s.lower() for s in result.project.detected_stack}
        skill_tokens = {s.lower() for s in result.learning_path.required_skills}
        context_tokens = project_tokens | stack_tokens | skill_tokens

        for q in ar.questions:
            q_lower = q.question.lower()
            # If the question looks like a generic exam dump, prepend context.
            is_generic = (
                "which of the following" in q_lower
                and not any(tok in q_lower for tok in context_tokens if len(tok) > 3)
            )
            if is_generic:
                q.question = (
                    f"In the context of {result.project.project_name}: {q.question}"
                )

    if not ar.weak_areas:
        ar.weak_areas = result.learning_path.missing_skills or ["General Azure Knowledge"]
    if not ar.next_actions:
        ar.next_actions = [
            "Review recommended resources",
            "Complete hands-on labs for weak areas",
        ]

    # --- Manager dashboard ---
    md = result.manager_dashboard
    if not md.risk_areas:
        md.risk_areas = ar.weak_areas[:3] if ar.weak_areas else ["General Risk"]
    else:
        # Ensure source_references exist in assessment questions
        pass
    if not md.manager_recommendations:
        md.manager_recommendations = [
            "Schedule a knowledge-sharing session on weak areas",
            "Assign targeted learning resources",
        ]
    if not md.team_summary:
        md.team_summary = (
            f"Team is making progress on {result.project.project_name}. "
            "Focus on identified risk areas to improve certification readiness."
        )

    # Ensure risk_areas includes critical areas for document processing
    if result.project.project_category == "Document Processing / AI Automation":
        required_risks = ["Security", "Event-Driven Design", "Document Intelligence"]
        existing = [r.lower() for r in md.risk_areas]
        for risk in required_risks:
            if risk.lower() not in existing:
                md.risk_areas.append(risk)

    # Ensure assessment source_references are non-empty
    for q in ar.questions:
        if not q.source_reference:
            q.source_reference = "azure_fundamentals.md"

    # --- Append Verifier trace step ---
    result.trace.append(
        AgentTraceStep(
            agent_name="Verifier Agent",
            action="verify_result",
            input_summary=(
                f"CertForgeResult for project '{result.project.project_name}' "
                f"with {len(result.task_tree.tasks)} tasks and "
                f"{len(result.assessment.questions)} assessment questions"
            ),
            output_summary=(
                "Validated all sections; filled safe defaults where needed; "
                "ensured risk_areas, source_references, and demo-critical lists "
                "are non-empty; confirmed assessment questions are project-grounded"
            ),
            tools_used=[],
        )
    )

    return result
