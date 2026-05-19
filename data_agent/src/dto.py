from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class AuditEventDTO:
    user_id: str | None
    trace_id: str
    role: str
    metric: str
    metric_version: str
    sql: str
    execution_mode: str
    row_count: int
    logged_at: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PipelineResultDTO:
    user_id: str | None
    query_object: Dict[str, Any]
    logic_form: Dict[str, Any]
    trace_id: str
    sql: str
    execution: Dict[str, Any]
    explain: Dict[str, Any]
    audit_event: AuditEventDTO | None = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        # keep backward compatibility for current API response shape
        payload.pop("audit_event", None)
        return payload
