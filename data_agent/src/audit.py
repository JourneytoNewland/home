from __future__ import annotations

from typing import Any, Dict, List, Optional


class AuditStore:
    """In-memory audit replay store.

    Supports filtering by trace_id, user_id, role, metric.
    """

    def __init__(self, events: List[Dict[str, Any]] | None = None):
        self._events: List[Dict[str, Any]] = list(events or [])

    def append(self, event: Dict[str, Any]) -> None:
        self._events.append(dict(event))

    def query(
        self,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        metric: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = self._events
        if trace_id is not None:
            results = [e for e in results if e.get("trace_id") == trace_id]
        if user_id is not None:
            results = [e for e in results if e.get("user_id") == user_id]
        if role is not None:
            results = [e for e in results if e.get("role") == role]
        if metric is not None:
            results = [e for e in results if e.get("metric") == metric]
        return list(results)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)
