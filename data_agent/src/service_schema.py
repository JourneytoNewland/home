from __future__ import annotations

from typing import Any, Dict, List

from data_agent.src.errors import DataAgentError


REQUIRED_KEYS = {
    "code": str,
    "message": str,
    "items": list,
    "total": int,
    "limit": (int, type(None)),
    "offset": int,
    "next_offset": (int, type(None)),
}


def validate_audit_service_response(payload: Dict[str, Any]) -> None:
    for key, expected in REQUIRED_KEYS.items():
        if key not in payload:
            raise DataAgentError(f"service response missing key: {key}")
        if not isinstance(payload[key], expected):
            raise DataAgentError(f"service response invalid type for key '{key}'")

    items: List[Any] = payload["items"]
    for item in items:
        if not isinstance(item, dict):
            raise DataAgentError("service response items must be list[dict]")
        if "trace_id" not in item or "role" not in item or "metric" not in item:
            raise DataAgentError("service response item missing required fields")
