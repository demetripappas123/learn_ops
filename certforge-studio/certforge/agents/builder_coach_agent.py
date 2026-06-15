"""Builder Coach Agent: generates a step-by-step BuilderWorkflow for a given TaskNode."""

from __future__ import annotations

from certforge.schemas.models import BuilderWorkflow, LearningPath, ProjectDefinition, TaskNode
from certforge.tools.retrieval_tool import retrieve_knowledge

_MANAGED_IDENTITY_TASK_TITLE = "Secure access with Entra ID and managed identity"


def _is_managed_identity_task(task: TaskNode) -> bool:
    return task.title.strip().lower() == _MANAGED_IDENTITY_TASK_TITLE.lower()


def generate_builder_workflow(
    task: TaskNode,
    project: ProjectDefinition,
    learning_path: LearningPath,
) -> BuilderWorkflow:
    """Return a BuilderWorkflow tailored to the supplied TaskNode and project context."""

    if _is_managed_identity_task(task):
        return _managed_identity_workflow(task, project, learning_path)

    return _generic_workflow(task, project, learning_path)


# ---------------------------------------------------------------------------
# Managed-identity specialisation
# ---------------------------------------------------------------------------

def _managed_identity_workflow(
    task: TaskNode,
    project: ProjectDefinition,
    learning_path: LearningPath,
) -> BuilderWorkflow:
    ide_copilot_prompt = (
        f"I am building '{project.project_name}'. "
        "Help me configure managed identity and DefaultAzureCredential so that "
        "Azure Functions and other services authenticate to Azure Blob Storage, "
        "Azure AI Document Intelligence, and Azure AI Search without storing "
        "any connection strings or secrets in configuration files. "
        "Apply RBAC least-privilege role assignments (e.g. Storage Blob Data Reader, "
        "Cognitive Services User) and show me how to enable a system-assigned managed "
        "identity on the Function App via Bicep or the Azure CLI. "
        "Do NOT use connection strings, SAS tokens, or account keys."
    )

    concept_explanation = _build_concept_explanation(
        task,
        extra_query="managed identity DefaultAzureCredential RBAC least privilege",
    )

    return BuilderWorkflow(
        selected_task_id=task.task_id,
        selected_task_title=task.title,
        implementation_steps=[
            "Enable a system-assigned managed identity on the Azure Function App "
            "(Portal: Identity blade → Status On, or CLI: `az functionapp identity assign`).",
            "Assign the Storage Blob Data Reader role to the managed identity on the "
            "Blob Storage account using Azure RBAC.",
            "Assign the Cognitive Services User role to the managed identity on the "
            "Azure AI Document Intelligence resource.",
            "Assign the Search Index Data Contributor role on the Azure AI Search "
            "resource to the managed identity.",
            "Replace any connection-string usage in application code with "
            "`DefaultAzureCredential` from the `azure-identity` SDK "
            "(e.g. `BlobServiceClient(account_url=..., credential=DefaultAzureCredential())`).",
            "Remove all secrets/connection strings from `local.settings.json` and "
            "App Service application settings; use Managed Identity for production and "
            "`AzureCliCredential` locally during development.",
            "Validate with `az role assignment list` that only the required roles are "
            "assigned and run the application to confirm no authentication errors.",
        ],
        ide_copilot_prompt=ide_copilot_prompt,
        concept_explanation=concept_explanation,
        validation_checklist=[
            "No connection strings, account keys, or SAS tokens appear in source code or config.",
            "System-assigned managed identity is enabled on the Function App.",
            "RBAC roles are scoped to individual resources (not subscription-wide).",
            "`DefaultAzureCredential` is used in all SDK client instantiations.",
            "Application deploys and authenticates successfully without secrets in settings.",
            "Key Vault (if used) is accessed via managed identity, not access policies with keys.",
        ],
        common_mistakes=[
            "Storing connection strings in environment variables or `local.settings.json` "
            "and then accidentally committing the file to source control.",
            "Assigning overly broad roles such as Owner or Contributor instead of the "
            "minimum required data-plane roles.",
            "Forgetting to enable the managed identity before creating role assignments, "
            "causing the principal to be unknown to Azure RBAC.",
            "Using `AzureCliCredential` in production instead of the managed identity "
            "credential, which fails in non-interactive environments.",
            "Not verifying that the role assignment has propagated (can take a few minutes) "
            "before testing the application.",
        ],
    )


# ---------------------------------------------------------------------------
# Generic workflow
# ---------------------------------------------------------------------------

def _generic_workflow(
    task: TaskNode,
    project: ProjectDefinition,
    learning_path: LearningPath,
) -> BuilderWorkflow:
    skill_context = ", ".join(task.related_skills[:3]) if task.related_skills else task.title

    ide_copilot_prompt = (
        f"I am working on the task '{task.title}' for the project '{project.project_name}'. "
        f"The relevant skills are: {skill_context}. "
        f"The milestone is '{task.milestone}'. "
        "Guide me through implementing this step, using Azure best practices. "
        "Show concrete code examples and highlight any security or performance considerations."
    )

    concept_explanation = _build_concept_explanation(task, extra_query=skill_context)

    implementation_steps = _derive_implementation_steps(task, project)
    validation_checklist = _derive_validation_checklist(task)
    common_mistakes = _derive_common_mistakes(task)

    return BuilderWorkflow(
        selected_task_id=task.task_id,
        selected_task_title=task.title,
        implementation_steps=implementation_steps,
        ide_copilot_prompt=ide_copilot_prompt,
        concept_explanation=concept_explanation,
        validation_checklist=validation_checklist,
        common_mistakes=common_mistakes,
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_concept_explanation(task: TaskNode, extra_query: str = "") -> str:
    """Return a short concept explanation, enriched by knowledge-base snippets where available."""
    query = f"{task.title} {extra_query}".strip()
    snippets = retrieve_knowledge(query, top_k=2)

    base = (
        f"This task covers '{task.title}' within the '{task.milestone}' milestone. "
        f"Key skills involved: {', '.join(task.related_skills) if task.related_skills else 'see task description'}. "
        f"Certification objectives addressed: "
        f"{', '.join(task.certification_mapping) if task.certification_mapping else 'AZ-204 / AI-102'}. "
    )

    if snippets:
        best = snippets[0]
        base += (
            f"Reference — {best.get('title', best.get('source', 'knowledge base'))}: "
            f"{best.get('snippet', '')[:300]}"
        )

    # Optional LLM enrichment (behind USE_FOUNDRY_LLM); falls back to the deterministic text.
    from certforge.foundry.enrich import enrich_concept
    return enrich_concept(task.title, task.related_skills, base)


def _derive_implementation_steps(task: TaskNode, project: ProjectDefinition) -> list[str]:
    """Return a minimal but non-empty ordered list of implementation steps."""
    steps = [
        f"Review the task description and acceptance criteria for '{task.title}'.",
        f"Identify the Azure services involved: {', '.join(project.detected_stack[:3])}.",
        "Create or update the required Azure resources via the Portal, CLI, or Bicep.",
        "Implement the application code, following the project's coding standards.",
        f"Satisfy the learning checkpoint: {task.learning_checkpoint}",
        "Run unit tests and integration tests to confirm correctness.",
        "Commit changes with a clear message referencing the task ID and milestone.",
    ]
    return steps


def _derive_validation_checklist(task: TaskNode) -> list[str]:
    return [
        f"All acceptance criteria for '{task.title}' are met.",
        "No hardcoded secrets or credentials appear in code or configuration.",
        "Relevant unit/integration tests pass without errors.",
        f"Assessment checkpoint satisfied: {task.assessment_checkpoint}",
        "Code is reviewed for adherence to project style guidelines.",
        "Azure resources are tagged and scoped to the correct resource group.",
    ]


def _derive_common_mistakes(task: TaskNode) -> list[str]:
    return [
        "Skipping dependency tasks before starting this one — check prerequisites first.",
        "Using subscription-scoped RBAC roles instead of resource-scoped assignments.",
        "Hard-coding configuration values that should come from environment variables or Key Vault.",
        "Neglecting to update the task's learning checkpoint documentation after completion.",
        "Forgetting to add or update tests when implementation logic changes.",
    ]
