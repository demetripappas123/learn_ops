from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectDefinition(BaseModel):
    project_name: str
    user_request: str
    project_category: str
    detected_stack: list[str] = Field(default_factory=list)
    target_certifications: list[str] = Field(default_factory=list)
    difficulty: str
    assumptions: list[str] = Field(default_factory=list)


class LearnerProfile(BaseModel):
    learner_id: str
    role: str
    experience_level: str
    known_skills: list[str] = Field(default_factory=list)
    target_certifications: list[str] = Field(default_factory=list)


class WorkloadSignal(BaseModel):
    learner_id: str
    meeting_hours_per_week: int
    focus_hours_per_week: int
    preferred_learning_slot: str
    workload_risk: str


class SkillMapping(BaseModel):
    skill: str
    certification: str
    confidence: float
    learner_status: str
    supporting_sources: list[str] = Field(default_factory=list)


class LearningPath(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommended_resources: list[str] = Field(default_factory=list)
    certification_objectives: list[str] = Field(default_factory=list)
    source_snippets: list[str] = Field(default_factory=list)


class TaskNode(BaseModel):
    task_id: str
    title: str
    description: str
    milestone: str
    dependencies: list[str] = Field(default_factory=list)
    related_skills: list[str] = Field(default_factory=list)
    certification_mapping: list[str] = Field(default_factory=list)
    estimated_effort: str
    learning_checkpoint: str
    assessment_checkpoint: str


class TaskTree(BaseModel):
    project_name: str
    milestones: list[str] = Field(default_factory=list)
    tasks: list[TaskNode] = Field(default_factory=list)


class BuilderWorkflow(BaseModel):
    selected_task_id: str
    selected_task_title: str
    implementation_steps: list[str] = Field(default_factory=list)
    ide_copilot_prompt: str
    concept_explanation: str
    validation_checklist: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)


class AssessmentQuestion(BaseModel):
    question: str
    expected_answer: str
    explanation: str
    certification_mapping: str
    skill_area: str
    source_reference: str


class AssessmentResult(BaseModel):
    readiness_score: int
    readiness_level: str
    questions: list[AssessmentQuestion] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class ManagerDashboard(BaseModel):
    project_progress_percent: int
    az204_coverage_percent: int
    ai102_coverage_percent: int
    risk_areas: list[str] = Field(default_factory=list)
    manager_recommendations: list[str] = Field(default_factory=list)
    team_summary: str


class AgentTraceStep(BaseModel):
    agent_name: str
    action: str
    input_summary: str
    output_summary: str
    tools_used: list[str] = Field(default_factory=list)


class CertForgeResult(BaseModel):
    project: ProjectDefinition
    learner_profile: LearnerProfile
    workload: WorkloadSignal
    learning_path: LearningPath
    task_tree: TaskTree
    builder_workflow: BuilderWorkflow
    assessment: AssessmentResult
    manager_dashboard: ManagerDashboard
    trace: list[AgentTraceStep] = Field(default_factory=list)
