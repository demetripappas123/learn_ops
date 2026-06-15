"""CLI runner for CertForge Studio.

Run from the certforge-studio directory:
    python main.py
"""
from __future__ import annotations

from certforge import config
from certforge.orchestrator import run_certforge_flow

config.load_env()

DEFAULT_USER_REQUEST = "I want to build an AI-powered document processing platform."


def _print_summary_rich(result) -> None:
    """Print a rich-formatted summary of the CertForge result."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    console = Console()

    # Project
    p = result.project
    console.print(Panel(
        f"[bold cyan]{p.project_name}[/bold cyan]\n"
        f"[dim]Category:[/dim] {p.project_category}\n"
        f"[dim]Difficulty:[/dim] {p.difficulty}\n"
        f"[dim]Stack:[/dim] {', '.join(p.detected_stack)}\n"
        f"[dim]Target Certs:[/dim] {', '.join(p.target_certifications)}\n"
        f"[dim]Assumptions:[/dim]\n" + "\n".join(f"  • {a}" for a in p.assumptions),
        title="[bold]Project Definition[/bold]",
        border_style="cyan",
    ))

    # Certifications & missing skills
    lp = result.learning_path
    console.print(Panel(
        f"[dim]Required Skills ({len(lp.required_skills)}):[/dim] "
        f"{', '.join(lp.required_skills[:8])}{'...' if len(lp.required_skills) > 8 else ''}\n\n"
        f"[bold red]Missing Skills ({len(lp.missing_skills)}):[/bold red]\n"
        + "\n".join(f"  • {s}" for s in lp.missing_skills[:6])
        + ("\n  ..." if len(lp.missing_skills) > 6 else "") + "\n\n"
        f"[dim]Certification Objectives:[/dim]\n"
        + "\n".join(f"  • {o}" for o in lp.certification_objectives),
        title="[bold]Learning Path[/bold]",
        border_style="green",
    ))

    # First few tasks
    tt = result.task_tree
    task_table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
    task_table.add_column("ID", style="dim", width=6)
    task_table.add_column("Title", width=42)
    task_table.add_column("Milestone", width=26)
    task_table.add_column("Effort", width=10)
    for task in tt.tasks[:5]:
        task_table.add_row(task.task_id, task.title, task.milestone, task.estimated_effort)
    if len(tt.tasks) > 5:
        task_table.add_row("...", f"({len(tt.tasks) - 5} more tasks)", "", "")
    console.print(Panel(task_table, title=f"[bold]Task Tree — {tt.project_name} ({len(tt.tasks)} tasks)[/bold]", border_style="magenta"))

    # Builder prompt
    bw = result.builder_workflow
    console.print(Panel(
        f"[bold]Task:[/bold] [{bw.selected_task_id}] {bw.selected_task_title}\n\n"
        f"[bold]IDE Copilot Prompt:[/bold]\n{bw.ide_copilot_prompt}\n\n"
        f"[bold]Implementation Steps:[/bold]\n"
        + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(bw.implementation_steps[:4]))
        + ("\n  ..." if len(bw.implementation_steps) > 4 else ""),
        title="[bold]Builder Coach Workflow[/bold]",
        border_style="yellow",
    ))

    # Assessment
    ar = result.assessment
    readiness_color = "green" if ar.readiness_score >= 80 else ("yellow" if ar.readiness_score >= 60 else "red")
    q_text = ""
    if ar.questions:
        q = ar.questions[0]
        q_text = (
            f"[bold]Q:[/bold] {q.question}\n"
            f"[dim]Cert:[/dim] {q.certification_mapping}  |  "
            f"[dim]Skill:[/dim] {q.skill_area}  |  "
            f"[dim]Source:[/dim] {q.source_reference}"
        )
    console.print(Panel(
        f"[bold]Readiness Score:[/bold] [{readiness_color}]{ar.readiness_score}/100 — {ar.readiness_level}[/{readiness_color}]\n"
        f"[dim]Weak Areas:[/dim] {', '.join(ar.weak_areas)}\n\n"
        f"[bold]Sample Question:[/bold]\n{q_text}\n\n"
        f"[bold]Next Actions:[/bold]\n"
        + "\n".join(f"  • {a}" for a in ar.next_actions),
        title="[bold]Assessment & Readiness[/bold]",
        border_style=readiness_color,
    ))

    # Manager dashboard
    md = result.manager_dashboard
    console.print(Panel(
        f"[bold]Progress:[/bold] {md.project_progress_percent}%  |  "
        f"[bold]AZ-204 Coverage:[/bold] {md.az204_coverage_percent}%  |  "
        f"[bold]AI-102 Coverage:[/bold] {md.ai102_coverage_percent}%\n\n"
        f"[bold red]Risk Areas:[/bold red] {', '.join(md.risk_areas)}\n\n"
        f"[bold]Recommendations:[/bold]\n"
        + "\n".join(f"  • {r}" for r in md.manager_recommendations) + "\n\n"
        f"[bold]Team Summary:[/bold]\n{md.team_summary}",
        title="[bold]Manager Dashboard[/bold]",
        border_style="blue",
    ))


def _print_summary_plain(result) -> None:
    """Fallback plain-text summary."""
    p = result.project
    print("=" * 70)
    print("PROJECT")
    print(f"  Name     : {p.project_name}")
    print(f"  Category : {p.project_category}")
    print(f"  Stack    : {', '.join(p.detected_stack)}")
    print(f"  Certs    : {', '.join(p.target_certifications)}")
    print(f"  Difficulty: {p.difficulty}")
    for a in p.assumptions:
        print(f"  Assumption: {a}")

    lp = result.learning_path
    print("\nLEARNING PATH")
    print(f"  Required Skills : {', '.join(lp.required_skills[:8])}")
    print(f"  Missing Skills  : {', '.join(lp.missing_skills[:6])}")
    for obj in lp.certification_objectives:
        print(f"  Objective: {obj}")

    tt = result.task_tree
    print(f"\nTASK TREE  ({len(tt.tasks)} tasks)")
    for task in tt.tasks[:5]:
        print(f"  [{task.task_id}] {task.title}  | {task.milestone}  | {task.estimated_effort}")
    if len(tt.tasks) > 5:
        print(f"  ... ({len(tt.tasks) - 5} more tasks)")

    bw = result.builder_workflow
    print(f"\nBUILDER COACH  [{bw.selected_task_id}] {bw.selected_task_title}")
    print(f"  IDE Prompt: {bw.ide_copilot_prompt[:200]}...")
    for i, s in enumerate(bw.implementation_steps[:3], 1):
        print(f"  {i}. {s}")

    ar = result.assessment
    print(f"\nASSESSMENT  Score={ar.readiness_score}/100  Level={ar.readiness_level}")
    print(f"  Weak Areas: {', '.join(ar.weak_areas)}")
    if ar.questions:
        q = ar.questions[0]
        print(f"  Q: {q.question}")
        print(f"     Cert={q.certification_mapping}  Skill={q.skill_area}  Source={q.source_reference}")
    for action in ar.next_actions:
        print(f"  Next: {action}")

    md = result.manager_dashboard
    print(f"\nMANAGER DASHBOARD")
    print(f"  Progress={md.project_progress_percent}%  AZ-204={md.az204_coverage_percent}%  AI-102={md.ai102_coverage_percent}%")
    print(f"  Risk Areas: {', '.join(md.risk_areas)}")
    for rec in md.manager_recommendations:
        print(f"  Rec: {rec}")
    print(f"  Summary: {md.team_summary}")
    print("=" * 70)


def main() -> None:
    """Entry point: run the CertForge pipeline and print a summary."""
    result = run_certforge_flow(user_request=DEFAULT_USER_REQUEST)

    try:
        _print_summary_rich(result)
    except ImportError:
        _print_summary_plain(result)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
