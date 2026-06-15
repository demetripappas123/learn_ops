"""Manager insights agent: generates a ManagerDashboard from project, task tree, and assessment data."""

from __future__ import annotations

import json
from pathlib import Path

from certforge.schemas.models import AssessmentResult, ManagerDashboard, ProjectDefinition, TaskTree

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def generate_manager_dashboard(
    project: ProjectDefinition,
    task_tree: TaskTree,
    assessment: AssessmentResult,
) -> ManagerDashboard:
    """Generate a ManagerDashboard using TEAM-A baseline from manager_progress.json and assessment weak areas."""
    with (_DATA_DIR / "manager_progress.json").open() as f:
        progress_data = json.load(f)

    team = progress_data["TEAM-A"]

    project_progress_percent: int = team["project_progress_percent"]
    az204_coverage_percent: int = team["az204_coverage_percent"]
    ai102_coverage_percent: int = team["ai102_coverage_percent"]

    # Build ordered de-duplicated union of TEAM-A risk_areas and assessment.weak_areas
    seen: set[str] = set()
    risk_areas: list[str] = []
    for area in team["risk_areas"] + assessment.weak_areas:
        if area not in seen:
            seen.add(area)
            risk_areas.append(area)

    # Ensure document-case mandatory risk areas are present (document projects only)
    if "document" in (project.project_category or "").lower():
        for required in ("Security", "Event-Driven Design", "Document Intelligence"):
            if required not in seen:
                seen.add(required)
                risk_areas.append(required)

    # Derive recommendations from completion patterns and risk areas
    manager_recommendations: list[str] = []
    for pattern in team.get("completion_patterns", []):
        manager_recommendations.append(pattern)
    if not manager_recommendations:
        manager_recommendations.append(
            "Prioritize security and identity tasks to improve AZ-204 coverage."
        )

    completed_tasks = len(task_tree.tasks)
    total_milestones = len(task_tree.milestones) if task_tree.milestones else 1
    team_summary = (
        f"Team is working on '{project.project_name}' targeting "
        f"{', '.join(project.target_certifications)}. "
        f"Current project progress: {project_progress_percent}% with "
        f"{completed_tasks} tasks across {total_milestones} milestones planned. "
        f"AZ-204 coverage is at {az204_coverage_percent}% and AI-102 at "
        f"{ai102_coverage_percent}%. Key risk areas: {', '.join(risk_areas[:3])}."
    )

    return ManagerDashboard(
        project_progress_percent=project_progress_percent,
        az204_coverage_percent=az204_coverage_percent,
        ai102_coverage_percent=ai102_coverage_percent,
        risk_areas=risk_areas,
        manager_recommendations=manager_recommendations,
        team_summary=team_summary,
    )
