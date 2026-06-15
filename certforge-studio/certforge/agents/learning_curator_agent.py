"""Learning Curator Agent: curates a LearningPath for a given project and learner."""

from __future__ import annotations

from certforge.schemas.models import LearnerProfile, LearningPath, ProjectDefinition
from certforge.tools.certification_mapper import get_certification_skills, map_stack_to_certifications
from certforge.tools.retrieval_tool import retrieve_knowledge


def curate_learning_path(project: ProjectDefinition, learner: LearnerProfile) -> LearningPath:
    """Return a LearningPath derived from the project's target certifications and the learner's known skills."""
    cert_info = get_certification_skills(project.target_certifications)
    stack_coverage = map_stack_to_certifications(project.detected_stack)

    required_skills: list[str] = []
    certification_objectives: list[str] = []

    for cert in project.target_certifications:
        info = cert_info.get(cert)
        if not info:
            continue
        # Required skills come from the certification's own objectives, not the stack.
        required_skills.extend(info["skills"])
        covered = stack_coverage.get(cert, [])
        covered_note = f" (covered by: {', '.join(covered)})" if covered else ""
        certification_objectives.append(
            f"{cert} – {info['name']}: {', '.join(info['skills'])}{covered_note}"
        )

    # Deduplicate while preserving order.
    seen: set[str] = set()
    deduped_required: list[str] = []
    for s in required_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            deduped_required.append(s)
    required_skills = deduped_required

    known_lower = {s.lower() for s in learner.known_skills}
    missing_skills = [s for s in required_skills if s.lower() not in known_lower]

    source_snippets: list[str] = []
    recommended_resources: list[str] = []

    for skill in missing_skills[:3]:
        results = retrieve_knowledge(skill, top_k=3)
        for r in results:
            snippet = r.get("snippet", "")
            source = r.get("source", "")
            if snippet and snippet not in source_snippets:
                source_snippets.append(snippet)
            if source and source not in recommended_resources:
                recommended_resources.append(source)

    return LearningPath(
        required_skills=required_skills,
        missing_skills=missing_skills,
        recommended_resources=recommended_resources,
        certification_objectives=certification_objectives,
        source_snippets=source_snippets,
    )
