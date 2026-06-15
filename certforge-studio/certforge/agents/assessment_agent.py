"""Assessment agent: generates grounded assessment questions and readiness scores."""

from __future__ import annotations

import re

from certforge.schemas.models import (
    AssessmentQuestion,
    AssessmentResult,
    LearningPath,
    ProjectDefinition,
    TaskNode,
)
from certforge.tools.readiness_scorer import calculate_readiness_score
from certforge.tools.retrieval_tool import retrieve_knowledge


_MANAGED_IDENTITY_QUESTION = AssessmentQuestion(
    question=(
        "Why should the document processing pipeline use managed identity "
        "instead of storing connection strings in configuration files?"
    ),
    expected_answer=(
        "Managed identity lets Azure services authenticate to other Azure resources "
        "without storing credentials anywhere. The identity is automatically managed "
        "by Azure AD, eliminating the risk of credential leakage through config files, "
        "source control, or logs."
    ),
    explanation=(
        "Hardcoded or config-file connection strings are a top cause of credential leaks. "
        "With managed identity, Azure handles token acquisition transparently via "
        "DefaultAzureCredential, and RBAC roles control the minimum required permissions."
    ),
    certification_mapping="AZ-204 / Security",
    skill_area="Security",
    source_reference="azure_security_basics.md",
)


def _base_questions_for_task(task: TaskNode, learning_path: LearningPath) -> list[AssessmentQuestion]:
    """Return 1-3 additional grounded questions derived from the task and learning path."""
    questions: list[AssessmentQuestion] = []

    # Try to ground questions in retrieved knowledge snippets
    skills_to_probe = task.related_skills[:2] if task.related_skills else learning_path.missing_skills[:2]

    for skill in skills_to_probe:
        hits = retrieve_knowledge(skill, top_k=1)
        source_ref = hits[0]["source"] if hits else "azure_security_basics.md"
        snippet = hits[0]["snippet"] if hits else ""

        if "blob" in skill.lower() or "storage" in skill.lower():
            questions.append(AssessmentQuestion(
                question=(
                    "What Azure service is used to store raw documents before they are "
                    "processed by Azure AI Document Intelligence, and why?"
                ),
                expected_answer=(
                    "Azure Blob Storage is used because it provides durable, scalable object "
                    "storage that integrates natively with Azure Functions via event triggers "
                    "and with Document Intelligence via SAS tokens or managed identity."
                ),
                explanation=(
                    f"Blob Storage is the standard landing zone for unstructured files in Azure. "
                    f"{snippet[:150].strip()}"
                ).strip(),
                certification_mapping="AZ-204 / Storage",
                skill_area="Azure Blob Storage",
                source_reference=source_ref,
            ))
        elif "function" in skill.lower() or "serverless" in skill.lower():
            questions.append(AssessmentQuestion(
                question=(
                    "How do Azure Functions enable event-driven document processing, "
                    "and what trigger type is most appropriate for reacting to new blobs?"
                ),
                expected_answer=(
                    "Azure Functions use a Blob Storage trigger that fires automatically when a "
                    "new file is uploaded. The function receives the blob stream and can pass it "
                    "to downstream services like Document Intelligence without polling."
                ),
                explanation=(
                    f"Event-driven patterns decouple ingestion from processing and scale "
                    f"automatically. {snippet[:150].strip()}"
                ).strip(),
                certification_mapping="AZ-204 / Serverless",
                skill_area="Azure Functions",
                source_reference=source_ref,
            ))
        elif "search" in skill.lower():
            questions.append(AssessmentQuestion(
                question=(
                    "What role does Azure AI Search play in the document processing pipeline "
                    "after extraction is complete?"
                ),
                expected_answer=(
                    "Azure AI Search indexes the extracted fields and text so users can run "
                    "full-text and semantic queries over the processed documents. It supports "
                    "vector search for AI-powered retrieval."
                ),
                explanation=(
                    f"Indexing extracted content enables downstream applications to search at "
                    f"scale. {snippet[:150].strip()}"
                ).strip(),
                certification_mapping="AI-102 / Knowledge Mining",
                skill_area="Azure AI Search",
                source_reference=source_ref,
            ))
        else:
            questions.append(AssessmentQuestion(
                question=(
                    f"Describe how '{skill}' is applied in the context of the task: "
                    f"'{task.title}'."
                ),
                expected_answer=(
                    f"'{skill}' is used to fulfil the goal described in '{task.title}' by "
                    "providing the necessary capability within the Azure platform, following "
                    "best practices for security, reliability, and performance."
                ),
                explanation=(
                    f"Understanding the role of each service helps map project tasks to "
                    f"certification objectives. {snippet[:100].strip()}"
                ).strip(),
                certification_mapping=", ".join(task.certification_mapping) if task.certification_mapping else "AZ-204",
                skill_area=skill,
                source_reference=source_ref,
            ))

        if len(questions) >= 2:
            break

    return questions


# Conceptual risk buckets used to summarise granular missing skills for non-document
# projects. weak_areas are MANAGER-FACING themes, not the raw missing-skill inventory
# (which stays on learning_path.missing_skills).
_CONCEPT_BUCKETS: list[tuple[tuple[str, ...], str]] = [
    (("security", "identity", "entra", "rbac", "managed identity"), "Security"),
    (("event", "function", "serverless", "trigger", "queue"), "Event-Driven Design"),
    (("document", "extraction", "ocr", "intelligence", "form"), "Document Intelligence"),
    (("search", "index", "rag", "retrieval", "knowledge"), "Search & Retrieval"),
    (("foundry", "openai", "responsible", "ai service", "integration"), "AI Service Integration"),
    (("monitor", "logging", "observability", "telemetry"), "Monitoring & Observability"),
]


def _needle_matches(needle: str, skill_lower: str, tokens: set[str]) -> bool:
    """Whole-word / prefix match so short needles like 'rag' do not match 'sto-rag-e'."""
    if " " in needle:
        return needle in skill_lower
    return any(tok == needle or tok.startswith(needle) for tok in tokens)


def _determine_weak_areas(task: TaskNode, learning_path: LearningPath, project: ProjectDefinition) -> list[str]:
    """Derive conceptual weak areas (manager-facing themes), not the raw missing-skill list."""
    category = (project.project_category or "").lower()
    if "document" in category:
        # Canonical demo risk areas for the document-processing platform.
        return ["Security", "Event-Driven Design", "Document Intelligence"]

    # For other project types, summarise missing skills into conceptual buckets.
    weak: list[str] = []
    for skill in learning_path.missing_skills:
        skill_lower = skill.lower()
        tokens = {t for t in re.split(r"[^a-z0-9]+", skill_lower) if t}
        for needles, concept in _CONCEPT_BUCKETS:
            if concept not in weak and any(_needle_matches(n, skill_lower, tokens) for n in needles):
                weak.append(concept)
    if not weak:
        weak = ["Security", "Monitoring & Observability"]
    return weak[:5]


def generate_assessment(
    task: TaskNode,
    learning_path: LearningPath,
    project: ProjectDefinition,
) -> AssessmentResult:
    """Generate a grounded assessment for the given task and learning context.

    Produces 2-4 original questions (not real exam items), computes a readiness
    score, derives weak areas, and recommends next actions.
    """
    weak_areas = _determine_weak_areas(task, learning_path, project)

    # Always include the managed-identity question
    questions: list[AssessmentQuestion] = [_MANAGED_IDENTITY_QUESTION]

    # Add task/skill-grounded questions (up to 3 more for a total of 2-4)
    extra = _base_questions_for_task(task, learning_path)
    questions.extend(extra[: 3])  # cap so total stays <= 4

    # Ensure we have at least 2 questions
    if len(questions) < 2:
        questions.append(AssessmentQuestion(
            question=(
                "What is the principle of least privilege and how does it apply to "
                "role assignments in this Azure project?"
            ),
            expected_answer=(
                "Least privilege means granting only the permissions required for a task. "
                "In Azure, this is enforced via RBAC by assigning narrow built-in roles "
                "(e.g., Storage Blob Data Reader) rather than Owner or Contributor."
            ),
            explanation=(
                "Over-privileged identities are a common attack vector. Scoping RBAC roles "
                "to specific resources limits blast radius if credentials are compromised."
            ),
            certification_mapping="AZ-204 / Security",
            skill_area="Security",
            source_reference="azure_security_basics.md",
        ))

    # Compute readiness score using the shared scorer
    readiness_score = calculate_readiness_score(None, learning_path, weak_areas)

    if readiness_score >= 80:
        readiness_level = "Exam Ready"
    elif readiness_score >= 60:
        readiness_level = "Developing"
    else:
        readiness_level = "Foundational"

    next_actions: list[str] = []
    if "Security" in weak_areas:
        next_actions.append("Complete the Azure security fundamentals module and review managed identity patterns.")
    if "Event-Driven Design" in weak_areas:
        next_actions.append("Practice implementing Azure Functions with Blob and Event Grid triggers.")
    if "Document Intelligence" in weak_areas:
        next_actions.append("Work through the Azure AI Document Intelligence quickstart and prebuilt model labs.")
    if not next_actions:
        next_actions.append(
            "Review certification objectives for "
            + ", ".join(project.target_certifications or ["AZ-204"])
            + " and attempt practice assessments."
        )

    return AssessmentResult(
        readiness_score=readiness_score,
        readiness_level=readiness_level,
        questions=questions,
        weak_areas=weak_areas,
        next_actions=next_actions,
    )
