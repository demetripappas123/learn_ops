"""Telemetry logger: appends agent trace steps as JSONL."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from certforge.schemas.models import AgentTraceStep

_TRACES_FILE = Path(__file__).parent.parent / "telemetry" / "traces.jsonl"


def log_trace(trace: list[AgentTraceStep], request_id: str | None = None) -> None:
    """Append one JSONL line to certforge/telemetry/traces.jsonl (best-effort).

    Telemetry must never break the agent pipeline, so any filesystem error
    (e.g. a read-only runtime) is swallowed after a best-effort attempt.
    """
    record = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps": [s.model_dump() for s in trace],
    }
    try:
        _TRACES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _TRACES_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        # Best-effort telemetry: never let logging failures abort the flow.
        pass
