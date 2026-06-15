"""Map a technology stack to certifications via the certification matrix."""

from __future__ import annotations

import json
from pathlib import Path


def map_stack_to_certifications(stack: list[str]) -> dict:
    """Return a dict mapping cert name -> list of stack items that match its skills.

    Matching is case-insensitive substring: a stack item matches a cert skill if
    either string contains the other.
    """
    matrix_path = Path(__file__).parent.parent / "data" / "certification_matrix.json"
    matrix: dict = json.loads(matrix_path.read_text())

    result: dict[str, list[str]] = {}
    for cert, info in matrix.items():
        cert_skills: list[str] = info.get("skills", [])
        matched: list[str] = []
        for item in stack:
            item_lower = item.lower()
            for skill in cert_skills:
                skill_lower = skill.lower()
                if item_lower in skill_lower or skill_lower in item_lower:
                    matched.append(item)
                    break
        result[cert] = matched

    return result


def get_certification_skills(certifications: list[str]) -> dict:
    """Return {cert: {"name": str, "skills": list[str]}} from the certification matrix.

    Unlike map_stack_to_certifications (which maps a *stack* onto certs), this returns
    the authoritative skill objectives for each certification — used to build the
    learner's required-skill set so real objectives (e.g. Managed identity, Monitoring,
    Event-driven architecture) are never dropped.
    """
    matrix_path = Path(__file__).parent.parent / "data" / "certification_matrix.json"
    matrix: dict = json.loads(matrix_path.read_text())

    info: dict[str, dict] = {}
    for cert in certifications:
        entry = matrix.get(cert)
        if entry:
            info[cert] = {
                "name": entry.get("name", cert),
                "skills": list(entry.get("skills", [])),
            }
    return info
