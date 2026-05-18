from __future__ import annotations

from typing import Any, Dict, List, Optional
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
