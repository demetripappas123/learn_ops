"""Task tree generator for CertForge Studio."""

from __future__ import annotations

from certforge.schemas.models import TaskNode


def create_document_processing_task_tree(project_name: str) -> list[TaskNode]:
    """Return >=12 TaskNodes across 7 milestones for the document processing project."""
    tasks = [
        # Milestone 1: Architecture and Requirements
        TaskNode(
            task_id="T01",
            title="Define solution architecture and requirements",
            description=(
                "Document the end-to-end architecture for the AI-powered document processing "
                "platform. Identify ingestion paths, processing stages, AI services, storage "
                "layers, and integration points. Capture non-functional requirements (scale, "
                "latency, security)."
            ),
            milestone="Architecture and Requirements",
            dependencies=[],
            related_skills=["Solution Architecture", "Azure AI Foundry", "Requirements Analysis"],
            certification_mapping=["AZ-204: Design Azure solutions", "AI-102: Plan an AI solution"],
            estimated_effort="4 hours",
            learning_checkpoint=(
                "Review Azure Well-Architected Framework pillars relevant to AI workloads."
            ),
            assessment_checkpoint=(
                "Can you describe the data flow from document upload to structured extraction?"
            ),
        ),
        TaskNode(
            task_id="T02",
            title="Identify target document types and extraction schema",
            description=(
                "Catalogue the document types to be processed (invoices, forms, PDFs). Define "
                "the extraction schema (fields, confidence thresholds, output format) that will "
                "guide Azure AI Document Intelligence model selection."
            ),
            milestone="Architecture and Requirements",
            dependencies=["T01"],
            related_skills=["Azure AI Document Intelligence", "Data Modelling", "OCR"],
            certification_mapping=[
                "AI-102: Analyze documents with Document Intelligence",
                "AI-102: Plan a Document Intelligence solution",
            ],
            estimated_effort="2 hours",
            learning_checkpoint=(
                "Study Document Intelligence prebuilt models (invoice, receipt, general document)."
            ),
            assessment_checkpoint=(
                "Which prebuilt model best suits invoice extraction and why?"
            ),
        ),
        # Milestone 2: Storage and Ingestion
        TaskNode(
            task_id="T03",
            title="Provision Azure Blob Storage and container hierarchy",
            description=(
                "Create the Blob Storage account and define container structure: raw-uploads, "
                "processing-queue, processed-output, failed-documents. Configure lifecycle "
                "management policies and access tiers."
            ),
            milestone="Storage and Ingestion",
            dependencies=["T01"],
            related_skills=["Azure Blob Storage", "Storage Account Configuration", "Lifecycle Policies"],
            certification_mapping=[
                "AZ-204: Develop solutions that use Blob Storage",
                "AZ-204: Implement Azure storage security",
            ],
            estimated_effort="2 hours",
            learning_checkpoint=(
                "Read about Blob Storage tiers (Hot, Cool, Archive) and lifecycle rules."
            ),
            assessment_checkpoint=(
                "How would you automate moving processed blobs to Cool tier after 30 days?"
            ),
        ),
        TaskNode(
            task_id="T04",
            title="Implement document upload API and event trigger",
            description=(
                "Build the HTTP-triggered Azure Function that accepts document uploads, validates "
                "file type and size, writes the blob to raw-uploads container, and emits a "
                "Blob-created event to trigger downstream processing."
            ),
            milestone="Storage and Ingestion",
            dependencies=["T03"],
            related_skills=["Azure Functions", "Azure Blob Storage", "Event-Driven Design"],
            certification_mapping=[
                "AZ-204: Implement Azure Functions",
                "AZ-204: Develop event-based solutions",
            ],
            estimated_effort="4 hours",
            learning_checkpoint=(
                "Study Azure Functions HTTP trigger and Blob output binding patterns."
            ),
            assessment_checkpoint=(
                "Explain the difference between a Blob trigger and an Event Grid trigger for Functions."
            ),
        ),
        # Milestone 3: Serverless Processing
        TaskNode(
            task_id="T05",
            title="Build blob-triggered processing orchestrator function",
            description=(
                "Implement a Blob-triggered Azure Function that picks up documents from "
                "raw-uploads and orchestrates the pipeline: validate, route to AI extraction, "
                "write results, and move blobs to the correct output container."
            ),
            milestone="Serverless Processing",
            dependencies=["T04"],
            related_skills=["Azure Functions", "Event-Driven Design", "Orchestration Patterns"],
            certification_mapping=[
                "AZ-204: Implement Azure Functions",
                "AZ-204: Develop event-based solutions",
            ],
            estimated_effort="5 hours",
            learning_checkpoint=(
                "Review Durable Functions fan-out/fan-in patterns for parallel AI calls."
            ),
            assessment_checkpoint=(
                "When would you use Durable Functions instead of a simple Blob trigger?"
            ),
        ),
        TaskNode(
            task_id="T06",
            title="Configure Function App settings and deployment slots",
            description=(
                "Set up the Function App with consumption/premium plan, application settings "
                "(non-secret configuration), staging deployment slot, and slot-swap strategy "
                "for zero-downtime releases."
            ),
            milestone="Serverless Processing",
            dependencies=["T05"],
            related_skills=["Azure Functions", "Deployment Slots", "App Configuration"],
            certification_mapping=[
                "AZ-204: Implement Azure Functions",
                "AZ-204: Deploy Azure compute solutions",
            ],
            estimated_effort="2 hours",
            learning_checkpoint=(
                "Study Function App hosting plans and deployment slot swap mechanics."
            ),
            assessment_checkpoint=(
                "What is the risk of swapping slots without sticky settings configured?"
            ),
        ),
        # Milestone 4: AI Extraction
        TaskNode(
            task_id="T07",
            title="Integrate Azure AI Document Intelligence for field extraction",
            description=(
                "Connect the processing function to Azure AI Document Intelligence using the "
                "Python SDK. Submit documents to the appropriate prebuilt or custom model, "
                "parse the AnalyzeResult response, and persist extracted fields as structured JSON."
            ),
            milestone="AI Extraction",
            dependencies=["T05"],
            related_skills=["Azure AI Document Intelligence", "OCR", "Python SDK", "JSON"],
            certification_mapping=[
                "AI-102: Analyze documents with Document Intelligence",
                "AI-102: Extract data from forms and documents",
            ],
            estimated_effort="6 hours",
            learning_checkpoint=(
                "Work through the Document Intelligence Python SDK quickstart and AnalyzeResult schema."
            ),
            assessment_checkpoint=(
                "How do you handle low-confidence fields returned by Document Intelligence?"
            ),
        ),
        TaskNode(
            task_id="T08",
            title="Train and publish custom Document Intelligence model",
            description=(
                "Label training documents in Document Intelligence Studio, train a custom "
                "extraction model for domain-specific forms, evaluate accuracy, and publish "
                "the model endpoint for use in the processing pipeline."
            ),
            milestone="AI Extraction",
            dependencies=["T07"],
            related_skills=["Azure AI Document Intelligence", "Model Training", "Azure AI Foundry"],
            certification_mapping=[
                "AI-102: Build a custom Document Intelligence solution",
                "AI-102: Manage and monitor AI solutions",
            ],
            estimated_effort="8 hours",
            learning_checkpoint=(
                "Complete the Document Intelligence Studio labelling tutorial and review "
                "accuracy metrics (field accuracy, model confidence)."
            ),
            assessment_checkpoint=(
                "What minimum number of labelled samples is recommended for a reliable custom model?"
            ),
        ),
        # Milestone 5: Search and Retrieval
        TaskNode(
            task_id="T09",
            title="Index extracted documents in Azure AI Search",
            description=(
                "Create an Azure AI Search index schema matching the extraction output. Build "
                "an indexer that reads processed JSON from Blob Storage and populates the index. "
                "Enable semantic ranking for natural-language queries over extracted content."
            ),
            milestone="Search and Retrieval",
            dependencies=["T07"],
            related_skills=["Azure AI Search", "Indexing", "Semantic Search"],
            certification_mapping=[
                "AI-102: Implement an Azure AI Search solution",
                "AI-102: Enrich a search index",
            ],
            estimated_effort="4 hours",
            learning_checkpoint=(
                "Study AI Search indexer schedules, skillsets, and semantic configuration."
            ),
            assessment_checkpoint=(
                "How does semantic ranking differ from BM25 keyword ranking in AI Search?"
            ),
        ),
        TaskNode(
            task_id="T10",
            title="Expose search query API for downstream consumers",
            description=(
                "Build an HTTP-triggered Azure Function that wraps the AI Search query API, "
                "accepts filter and search parameters, enforces per-caller rate limiting, and "
                "returns paginated structured results."
            ),
            milestone="Search and Retrieval",
            dependencies=["T09"],
            related_skills=["Azure AI Search", "Azure Functions", "API Design"],
            certification_mapping=[
                "AZ-204: Implement Azure Functions",
                "AI-102: Implement an Azure AI Search solution",
            ],
            estimated_effort="3 hours",
            learning_checkpoint=(
                "Review AI Search query syntax (simple, full Lucene) and OData filter expressions."
            ),
            assessment_checkpoint=(
                "How would you restrict search results to documents a caller is authorised to see?"
            ),
        ),
        # Milestone 6: Security and Identity
        TaskNode(
            task_id="T11",
            title="Secure access with Entra ID and managed identity",
            description=(
                "Enable system-assigned managed identity on the Function App. Grant least-privilege "
                "RBAC roles: Storage Blob Data Contributor on the storage account, Cognitive "
                "Services User on Document Intelligence, and Search Index Data Contributor on "
                "AI Search. Remove all connection strings and access keys from application "
                "settings; authenticate with DefaultAzureCredential throughout the codebase."
            ),
            milestone="Security and Identity",
            dependencies=["T06", "T08", "T10"],
            related_skills=[
                "Microsoft Entra ID",
                "Managed Identity",
                "RBAC",
                "Azure Security",
                "DefaultAzureCredential",
            ],
            certification_mapping=[
                "AZ-204: Implement secure Azure solutions",
                "AZ-204: Implement authentication and authorisation",
                "AI-102: Secure AI services",
            ],
            estimated_effort="4 hours",
            learning_checkpoint=(
                "Study the Azure Identity SDK, DefaultAzureCredential chain, and RBAC built-in roles "
                "for Storage, Cognitive Services, and AI Search."
            ),
            assessment_checkpoint=(
                "Why should the document processing pipeline use managed identity instead of "
                "storing connection strings in configuration files?"
            ),
        ),
        TaskNode(
            task_id="T12",
            title="Apply network isolation and private endpoints",
            description=(
                "Configure Virtual Network integration for the Function App. Add private endpoints "
                "for Blob Storage and AI Search. Restrict public network access on all services "
                "and validate that Functions can still reach dependencies through the VNet."
            ),
            milestone="Security and Identity",
            dependencies=["T11"],
            related_skills=["Azure Networking", "Private Endpoints", "VNet Integration", "Azure Security"],
            certification_mapping=[
                "AZ-204: Implement secure Azure solutions",
                "AZ-204: Implement Azure security",
            ],
            estimated_effort="3 hours",
            learning_checkpoint=(
                "Read about Azure Private Link, private DNS zones, and VNet service endpoints."
            ),
            assessment_checkpoint=(
                "What DNS configuration is required for a private endpoint to resolve correctly?"
            ),
        ),
        # Milestone 7: Monitoring and Deployment
        TaskNode(
            task_id="T13",
            title="Instrument telemetry with Application Insights",
            description=(
                "Add the Application Insights SDK to all Functions. Configure structured logging, "
                "custom metrics (documents processed, extraction confidence distribution, errors), "
                "and distributed tracing across the Blob trigger → AI extraction → Search indexing "
                "pipeline."
            ),
            milestone="Monitoring and Deployment",
            dependencies=["T12"],
            related_skills=["Azure Monitor", "Application Insights", "Observability", "Distributed Tracing"],
            certification_mapping=[
                "AZ-204: Instrument solutions to support monitoring and logging",
                "AZ-204: Monitor and troubleshoot solutions",
            ],
            estimated_effort="3 hours",
            learning_checkpoint=(
                "Study Application Insights custom events, metrics, and the distributed tracing model."
            ),
            assessment_checkpoint=(
                "How do you correlate a Blob trigger invocation with the downstream AI Search indexer call?"
            ),
        ),
        TaskNode(
            task_id="T14",
            title="Create CI/CD pipeline and infrastructure-as-code",
            description=(
                "Author Bicep templates for all resources (storage, Function App, Document "
                "Intelligence, AI Search). Build a GitHub Actions pipeline with lint, unit-test, "
                "bicep-what-if, deploy-to-staging, integration-test, and slot-swap stages."
            ),
            milestone="Monitoring and Deployment",
            dependencies=["T13"],
            related_skills=["Azure Functions", "Bicep", "CI/CD", "GitHub Actions", "DevOps"],
            certification_mapping=[
                "AZ-204: Deploy Azure compute solutions",
                "AZ-204: Implement containerised solutions",
            ],
            estimated_effort="5 hours",
            learning_checkpoint=(
                "Review Bicep module patterns and GitHub Actions OIDC authentication to Azure."
            ),
            assessment_checkpoint=(
                "How do you prevent secrets from appearing in GitHub Actions logs during a Bicep deployment?"
            ),
        ),
    ]
    return tasks


def create_generic_task_tree(
    project_name: str,
    milestones: list[str],
    required_skills: list[str],
) -> list[TaskNode]:
    """Return >=1 task per milestone (>=5 total) for non-document projects."""
    skill_str = ", ".join(required_skills[:3]) if required_skills else "Azure Services"

    milestone_templates = [
        {
            "title": "Define architecture and requirements",
            "description": (
                f"Document the solution architecture for {project_name}. "
                f"Identify required Azure services, integration points, and non-functional requirements. "
                f"Core skills involved: {skill_str}."
            ),
            "related_skills": required_skills[:3] if required_skills else ["Solution Architecture"],
            "certification_mapping": ["AZ-204: Design Azure solutions"],
            "estimated_effort": "3 hours",
            "learning_checkpoint": "Review Azure Well-Architected Framework pillars.",
            "assessment_checkpoint": "Can you describe the end-to-end data flow for this solution?",
        },
        {
            "title": "Provision core Azure services",
            "description": (
                f"Create and configure the core Azure resources needed by {project_name}. "
                "Apply naming conventions, resource tags, and least-privilege access from the start."
            ),
            "related_skills": required_skills[1:4] if len(required_skills) > 1 else ["Azure Resource Manager"],
            "certification_mapping": ["AZ-204: Deploy Azure compute solutions"],
            "estimated_effort": "3 hours",
            "learning_checkpoint": "Study Azure resource naming conventions and tagging strategies.",
            "assessment_checkpoint": "How do you enforce consistent resource tags across a subscription?",
        },
        {
            "title": "Implement core service logic",
            "description": (
                f"Build the primary application logic for {project_name} using the chosen Azure "
                f"services. Focus on correctness, error handling, and testability."
            ),
            "related_skills": required_skills[:4] if required_skills else ["Azure Functions"],
            "certification_mapping": ["AZ-204: Implement Azure solutions"],
            "estimated_effort": "6 hours",
            "learning_checkpoint": "Review SDK best practices and retry/back-off patterns.",
            "assessment_checkpoint": "How do you handle transient failures in Azure SDK calls?",
        },
        {
            "title": "Secure access with managed identity and RBAC",
            "description": (
                "Enable managed identity on compute resources and assign least-privilege RBAC roles. "
                "Remove any hardcoded credentials; use DefaultAzureCredential for all service calls."
            ),
            "related_skills": ["Microsoft Entra ID", "Managed Identity", "RBAC", "Azure Security"],
            "certification_mapping": [
                "AZ-204: Implement secure Azure solutions",
                "AZ-204: Implement authentication and authorisation",
            ],
            "estimated_effort": "3 hours",
            "learning_checkpoint": "Study DefaultAzureCredential chain and RBAC built-in roles.",
            "assessment_checkpoint": "Why is managed identity preferred over connection strings?",
        },
        {
            "title": "Add monitoring and deploy to production",
            "description": (
                f"Instrument {project_name} with Application Insights. Build a CI/CD pipeline "
                "using GitHub Actions and infrastructure-as-code (Bicep). Deploy to staging, "
                "run integration tests, then promote to production."
            ),
            "related_skills": ["Azure Monitor", "Application Insights", "CI/CD", "Bicep"],
            "certification_mapping": [
                "AZ-204: Instrument solutions to support monitoring",
                "AZ-204: Deploy Azure compute solutions",
            ],
            "estimated_effort": "4 hours",
            "learning_checkpoint": "Review Application Insights custom metrics and GitHub Actions OIDC auth.",
            "assessment_checkpoint": "How do you alert on error rate spikes in Application Insights?",
        },
    ]

    tasks: list[TaskNode] = []
    used_milestones = milestones if milestones else [t["title"] for t in milestone_templates]

    for i, milestone in enumerate(used_milestones):
        template_idx = i % len(milestone_templates)
        tmpl = milestone_templates[template_idx]
        task_id = f"T{str(i + 1).zfill(2)}"
        prev_id = f"T{str(i).zfill(2)}" if i > 0 else None

        tasks.append(
            TaskNode(
                task_id=task_id,
                title=tmpl["title"],
                description=tmpl["description"],
                milestone=milestone,
                dependencies=[prev_id] if prev_id else [],
                related_skills=tmpl["related_skills"],
                certification_mapping=tmpl["certification_mapping"],
                estimated_effort=tmpl["estimated_effort"],
                learning_checkpoint=tmpl["learning_checkpoint"],
                assessment_checkpoint=tmpl["assessment_checkpoint"],
            )
        )

    # Guarantee at least 5 tasks by padding with extra implementation tasks if needed.
    while len(tasks) < 5:
        idx = len(tasks)
        prev_id = tasks[-1].task_id if tasks else None
        tasks.append(
            TaskNode(
                task_id=f"T{str(idx + 1).zfill(2)}",
                title=f"Implementation task {idx + 1}",
                description=(
                    f"Additional implementation work for {project_name} covering "
                    f"{', '.join(required_skills[:2]) if required_skills else 'Azure services'}."
                ),
                milestone=used_milestones[-1] if used_milestones else "Implementation",
                dependencies=[prev_id] if prev_id else [],
                related_skills=required_skills[:3] if required_skills else ["Azure Services"],
                certification_mapping=["AZ-204: Implement Azure solutions"],
                estimated_effort="2 hours",
                learning_checkpoint="Review relevant Azure service documentation.",
                assessment_checkpoint="Can you explain the key design decisions made in this task?",
            )
        )

    return tasks
