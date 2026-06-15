"""Project Planner Agent: generates a TaskTree from a ProjectDefinition and LearningPath."""

from certforge.schemas.models import (
    LearningPath,
    ProjectDefinition,
    TaskTree,
    WorkloadSignal,
)
from certforge.tools.task_tree_generator import (
    create_document_processing_task_tree,
    create_generic_task_tree,
)

_GENERIC_MILESTONES = [
    "Architecture and Requirements",
    "Core Services",
    "Implementation",
    "Security and Identity",
    "Testing and Monitoring",
]


def generate_project_task_tree(
    project: ProjectDefinition,
    learning_path: LearningPath,
    workload: WorkloadSignal,
) -> TaskTree:
    """Generate a TaskTree for the given project, learning path, and workload signal."""
    is_document = project.project_category == "Document Processing / AI Automation"

    if is_document:
        tasks = create_document_processing_task_tree(project.project_name)
        milestones = [
            "Architecture and Requirements",
            "Storage and Ingestion",
            "Serverless Processing",
            "AI Extraction",
            "Search and Retrieval",
            "Security and Identity",
            "Monitoring and Deployment",
        ]
    else:
        milestones = _GENERIC_MILESTONES
        tasks = create_generic_task_tree(
            project.project_name,
            milestones,
            learning_path.required_skills,
        )

    return TaskTree(
        project_name=project.project_name,
        milestones=milestones,
        tasks=tasks,
    )
