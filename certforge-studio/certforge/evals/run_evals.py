"""Eval runner for CertForge. Run via: python -m certforge.evals.run_evals"""
from __future__ import annotations

import sys
from pathlib import Path

from certforge.orchestrator import run_certforge_flow

EVAL_CASES_PATH = Path(__file__).parent / "eval_cases.json"


def _load_cases() -> list[dict]:
    import json
    return json.loads(EVAL_CASES_PATH.read_text())


def _run_case(case: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []

    result = run_certforge_flow(case["user_request"])

    # expected_certifications all in result.project.target_certifications
    for cert in case.get("expected_certifications", []):
        if cert not in result.project.target_certifications:
            failures.append(
                f"Missing certification '{cert}' in target_certifications: {result.project.target_certifications}"
            )

    # expected_services appear (case-insensitive substring) in result.project.detected_stack
    detected_lower = [s.lower() for s in result.project.detected_stack]
    for svc in case.get("expected_services", []):
        svc_lower = svc.lower()
        if not any(svc_lower in d for d in detected_lower):
            failures.append(
                f"Service '{svc}' not found (case-insensitive) in detected_stack: {result.project.detected_stack}"
            )

    # len(result.task_tree.tasks) >= min_tasks
    min_tasks = case.get("min_tasks", 0)
    actual_tasks = len(result.task_tree.tasks)
    if actual_tasks < min_tasks:
        failures.append(
            f"task_tree has {actual_tasks} tasks, expected >= {min_tasks}"
        )

    # result.assessment.questions is non-empty
    if not result.assessment.questions:
        failures.append("assessment.questions is empty")

    # result.manager_dashboard exists (Pydantic will always construct it, but check it's not None)
    if result.manager_dashboard is None:
        failures.append("manager_dashboard is None")

    # every expected_risk_areas value in result.manager_dashboard.risk_areas
    for area in case.get("expected_risk_areas", []):
        if area not in result.manager_dashboard.risk_areas:
            failures.append(
                f"Risk area '{area}' not found in manager_dashboard.risk_areas: {result.manager_dashboard.risk_areas}"
            )

    passed = len(failures) == 0
    return passed, failures


def main() -> int:
    cases = _load_cases()
    passed_count = 0
    total = len(cases)

    for case in cases:
        name = case.get("name", case["user_request"])
        try:
            passed, failures = _run_case(case)
        except Exception as exc:
            passed = False
            failures = [f"Exception: {exc}"]

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            for f in failures:
                print(f"       - {f}")
        if passed:
            passed_count += 1

    print(f"\n{passed_count}/{total} passed")
    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
