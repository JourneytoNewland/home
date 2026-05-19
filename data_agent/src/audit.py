from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from data_agent.src.errors import AuditQueryError
from pathlib import Path
import json


class AuditStore:
    """In-memory audit replay store with optional JSONL persistence."""

    def __init__(self, events: List[Dict[str, Any]] | None = None, persist_path: str | None = None):
        self._events: List[Dict[str, Any]] = list(events or [])
        self.persist_path = persist_path
        if persist_path:
            self._load_from_file()

    def _load_from_file(self) -> None:
        p = Path(self.persist_path)
        if not p.exists():
            return
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            self._events.append(json.loads(line))

    def append(self, event: Dict[str, Any]) -> None:
        payload = dict(event)
        self._events.append(payload)
        if self.persist_path:
            p = Path(self.persist_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def query(
        self,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        metric: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        sort_by: str = "logged_at",
        sort_order: str = "desc",
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
        if start_time is not None:
            try:
                st = datetime.fromisoformat(start_time)
            except ValueError as exc:
                raise AuditQueryError(f"Invalid start_time format: {start_time}") from exc
            results = [e for e in results if "logged_at" in e and datetime.fromisoformat(e["logged_at"]) >= st]
        if end_time is not None:
            try:
                et = datetime.fromisoformat(end_time)
            except ValueError as exc:
                raise AuditQueryError(f"Invalid end_time format: {end_time}") from exc
            results = [e for e in results if "logged_at" in e and datetime.fromisoformat(e["logged_at"]) <= et]

        if offset < 0:
            raise AuditQueryError("offset must be >= 0")
        if limit is not None and limit < 0:
            raise AuditQueryError("limit must be >= 0")


        if sort_by != "logged_at":
            raise AuditQueryError("sort_by must be 'logged_at'")
        if sort_order not in {"asc", "desc"}:
            raise AuditQueryError("sort_order must be 'asc' or 'desc'")

        reverse = sort_order == "desc"

        def _sort_key(event: Dict[str, Any]) -> datetime:
            value = event.get("logged_at")
            if value is None:
                return datetime.min
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return datetime.min

        results = sorted(results, key=_sort_key, reverse=reverse)

        results = results[offset:]
        if limit is not None:
            results = results[:limit]
        return list(results)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)
