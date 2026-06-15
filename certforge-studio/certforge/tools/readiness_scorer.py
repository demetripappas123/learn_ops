"""Readiness scorer tool: computes a certification readiness score from assessment signals."""

from certforge.schemas.models import LearningPath, TaskTree


def calculate_readiness_score(task_tree: TaskTree | None, learning_path: LearningPath, weak_areas: list[str]) -> int:
    """Start at 70 and deduct points for weak areas; clamp result to 0..100."""
    score = 70

    for area in weak_areas:
        area_lower = area.lower()
        if "security" in area_lower:
            score -= 10
        if "event" in area_lower:
            score -= 10
        if "ai-102" in area_lower or "document intelligence" in area_lower or "extraction" in area_lower:
            score -= 10

    return max(0, min(100, score))
