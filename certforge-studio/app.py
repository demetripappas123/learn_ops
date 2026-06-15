"""CertForge Studio — Streamlit UI."""

from __future__ import annotations

import streamlit as st

from certforge import config
from certforge.orchestrator import run_certforge_flow

config.load_env()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CertForge Studio",
    page_icon="🎓",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("CertForge Studio")
    _iq = "Azure AI Search (Foundry IQ)" if config.use_foundry_iq() else "Local knowledge base"
    _llm = "Azure OpenAI (Foundry)" if config.use_foundry_llm() else "Deterministic"
    st.caption(f"Grounding: {_iq}  ·  Agents: {_llm}")
    st.markdown("---")

    learner_id = st.selectbox(
        "Learner",
        options=["EMP-001", "EMP-002", "EMP-003"],
        index=0,
    )

    scenario_map = {
        "AI-powered document processing platform": "build an AI-powered document processing platform with OCR and forms extraction",
        "RAG support assistant": "build a RAG support assistant with retrieval-augmented generation and knowledge chatbot",
        "Serverless API platform": "build a serverless API platform with Azure Functions and API Management endpoints",
    }

    scenario_label = st.selectbox(
        "Demo Scenario",
        options=list(scenario_map.keys()),
        index=0,
    )

    run_clicked = st.button("Run", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Session state — persist result across rerenders
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state["result"] = None
if "selected_task_id" not in st.session_state:
    st.session_state["selected_task_id"] = None

# ---------------------------------------------------------------------------
# Run flow when button pressed
# ---------------------------------------------------------------------------
if run_clicked:
    user_request = scenario_map[scenario_label]
    with st.spinner("Running CertForge agents…"):
        result = run_certforge_flow(
            user_request=user_request,
            learner_id=learner_id,
            selected_task_id=None,
        )
    st.session_state["result"] = result
    # Default to first task
    if result.task_tree.tasks:
        st.session_state["selected_task_id"] = result.task_tree.tasks[0].task_id
    else:
        st.session_state["selected_task_id"] = None

result = st.session_state.get("result")

# ---------------------------------------------------------------------------
# Main panel — only render when a result exists
# ---------------------------------------------------------------------------
if result is None:
    st.info("Select a learner and scenario, then press **Run** to generate a CertForge plan.")
    st.stop()

# ── Section 1: Project Analysis ──────────────────────────────────────────────
st.header("1  Project Analysis")
proj = result.project
col1, col2, col3 = st.columns(3)
col1.metric("Project", proj.project_name)
col2.metric("Category", proj.project_category)
col3.metric("Difficulty", proj.difficulty)

st.markdown("**Detected Stack**")
st.write(", ".join(proj.detected_stack) if proj.detected_stack else "—")

st.markdown("**Target Certifications**")
st.write(", ".join(proj.target_certifications) if proj.target_certifications else "—")

if proj.assumptions:
    with st.expander("Assumptions"):
        for a in proj.assumptions:
            st.markdown(f"- {a}")

# ── Section 2: Learning + Certification Map ───────────────────────────────────
st.header("2  Learning + Certification Map")
lp = result.learning_path

lcol1, lcol2 = st.columns(2)
with lcol1:
    st.markdown("**Required Skills**")
    for s in lp.required_skills:
        st.markdown(f"- {s}")
    st.markdown("**Missing Skills**")
    for s in lp.missing_skills:
        st.markdown(f"- {s}")
with lcol2:
    st.markdown("**Certification Objectives**")
    for obj in lp.certification_objectives:
        st.markdown(f"- {obj}")
    st.markdown("**Recommended Resources**")
    for r in lp.recommended_resources:
        st.markdown(f"- {r}")

if lp.source_snippets:
    with st.expander("Knowledge Snippets"):
        for snip in lp.source_snippets:
            st.markdown(snip)
            st.markdown("---")

# ── Section 3: Project Task Tree ─────────────────────────────────────────────
st.header("3  Project Task Tree")
tree = result.task_tree

if tree.milestones:
    st.markdown("**Milestones:** " + " → ".join(tree.milestones))

# Task selector
task_options = {t.task_id: f"{t.task_id}: {t.title}" for t in tree.tasks}

if task_options:
    chosen_task_id = st.selectbox(
        "Select a task to explore",
        options=list(task_options.keys()),
        format_func=lambda tid: task_options[tid],
        index=list(task_options.keys()).index(st.session_state["selected_task_id"])
        if st.session_state["selected_task_id"] in task_options
        else 0,
        key="task_selectbox",
    )
    st.session_state["selected_task_id"] = chosen_task_id

    # Expandable task cards grouped by milestone
    milestone_order = tree.milestones if tree.milestones else []
    tasks_by_milestone: dict[str, list] = {}
    for t in tree.tasks:
        tasks_by_milestone.setdefault(t.milestone, []).append(t)

    # Render in milestone order, then any stragglers
    rendered_milestones = []
    for ms in milestone_order:
        if ms in tasks_by_milestone:
            rendered_milestones.append(ms)
    for ms in tasks_by_milestone:
        if ms not in rendered_milestones:
            rendered_milestones.append(ms)

    for ms in rendered_milestones:
        st.subheader(ms)
        for task in tasks_by_milestone.get(ms, []):
            with st.expander(f"{task.task_id}: {task.title}"):
                st.markdown(f"**Description:** {task.description}")
                st.markdown(f"**Estimated Effort:** {task.estimated_effort}")
                if task.related_skills:
                    st.markdown("**Related Skills:** " + ", ".join(task.related_skills))
                if task.certification_mapping:
                    st.markdown("**Certifications:** " + ", ".join(task.certification_mapping))
                if task.dependencies:
                    st.markdown("**Dependencies:** " + ", ".join(task.dependencies))
                st.markdown(f"**Learning Checkpoint:** {task.learning_checkpoint}")
                st.markdown(f"**Assessment Checkpoint:** {task.assessment_checkpoint}")

# ── Section 4: Builder Coach ──────────────────────────────────────────────────
st.header("4  Builder Coach")

selected_task_obj = None
for t in tree.tasks:
    if t.task_id == st.session_state.get("selected_task_id"):
        selected_task_obj = t
        break

if selected_task_obj is not None:
    # Re-run builder coach for the selected task using cached result when
    # the task matches the result already computed, otherwise re-invoke.
    bw = result.builder_workflow
    if bw.selected_task_id != selected_task_obj.task_id:
        with st.spinner(f"Generating builder workflow for {selected_task_obj.task_id}…"):
            from certforge.agents.builder_coach_agent import generate_builder_workflow
            from certforge.agents.assessment_agent import generate_assessment

            bw = generate_builder_workflow(selected_task_obj, result.project, result.learning_path)
    st.subheader(f"Task: {bw.selected_task_title}")

    st.markdown("**Implementation Steps**")
    for i, step in enumerate(bw.implementation_steps, 1):
        st.markdown(f"{i}. {step}")

    st.markdown("**IDE Copilot Prompt**")
    st.code(bw.ide_copilot_prompt, language="text")

    with st.expander("Concept Explanation"):
        st.markdown(bw.concept_explanation)

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        st.markdown("**Validation Checklist**")
        for item in bw.validation_checklist:
            st.markdown(f"- [ ] {item}")
    with bcol2:
        st.markdown("**Common Mistakes**")
        for item in bw.common_mistakes:
            st.markdown(f"- {item}")
else:
    st.info("Select a task in Section 3 to view builder guidance.")

# ── Section 5: Assessment ─────────────────────────────────────────────────────
st.header("5  Assessment")
assessment = result.assessment

acol1, acol2 = st.columns(2)
acol1.metric("Readiness Score", f"{assessment.readiness_score}/100")
acol2.metric("Readiness Level", assessment.readiness_level)

if assessment.weak_areas:
    st.markdown("**Weak Areas:** " + ", ".join(assessment.weak_areas))

st.markdown("**Assessment Questions**")
for i, q in enumerate(assessment.questions, 1):
    with st.expander(f"Q{i}: {q.question}"):
        st.markdown(f"**Expected Answer:** {q.expected_answer}")
        st.markdown(f"**Explanation:** {q.explanation}")
        st.markdown(f"**Certification Mapping:** {q.certification_mapping}")
        st.markdown(f"**Skill Area:** {q.skill_area}")
        st.markdown(f"**Source Reference:** `{q.source_reference}`")

if assessment.next_actions:
    st.markdown("**Next Actions**")
    for action in assessment.next_actions:
        st.markdown(f"- {action}")

# ── Section 6: Manager Dashboard ─────────────────────────────────────────────
st.header("6  Manager Dashboard")
dash = result.manager_dashboard

m1, m2, m3 = st.columns(3)
m1.metric("Project Progress", f"{dash.project_progress_percent}%")
m2.metric("AZ-204 Coverage", f"{dash.az204_coverage_percent}%")
m3.metric("AI-102 Coverage", f"{dash.ai102_coverage_percent}%")

if dash.risk_areas:
    st.markdown("**Risk Areas**")
    st.warning(" | ".join(dash.risk_areas))

if dash.manager_recommendations:
    st.markdown("**Manager Recommendations**")
    for rec in dash.manager_recommendations:
        st.markdown(f"- {rec}")

if dash.team_summary:
    with st.expander("Team Summary"):
        st.markdown(dash.team_summary)

# ── Section 7: Agent Trace ────────────────────────────────────────────────────
st.header("7  Agent Trace")
st.caption("Safe trace summaries only — no chain-of-thought or internal reasoning.")

if result.trace:
    for step in result.trace:
        with st.expander(f"[{step.agent_name}] {step.action}"):
            st.markdown(f"**Input Summary:** {step.input_summary}")
            st.markdown(f"**Output Summary:** {step.output_summary}")
            if step.tools_used:
                st.markdown("**Tools Used:** " + ", ".join(step.tools_used))
else:
    st.info("No trace steps recorded.")
