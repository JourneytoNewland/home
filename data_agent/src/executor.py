from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from datetime import datetime, timezone
import sqlite3


class ExecutionError(RuntimeError):
    pass


@dataclass
class QueryExecutor:
    mode: str = "dry_run"
    sqlite_path: str = ":memory:"

    def execute(self, sql: str) -> Dict[str, Any]:
        if self.mode == "dry_run":
            return {"mode": "dry_run", "row_count": 0, "rows": []}

        if self.mode == "sqlite_readonly":
            if not self._is_select(sql):
                raise ExecutionError("Only SELECT statements are allowed in readonly mode.")
            rows = self._execute_sqlite(sql)
            return {"mode": "sqlite_readonly", "row_count": len(rows), "rows": rows}

        raise ExecutionError(f"Unsupported executor mode: {self.mode}")

    @staticmethod
    def _is_select(sql: str) -> bool:
        return sql.strip().lower().startswith("select")

    def _execute_sqlite(self, sql: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        finally:
            conn.close()


class AuditLogger:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def log(self, event: Dict[str, Any]) -> None:
        event = dict(event)
        event["logged_at"] = datetime.now(timezone.utc).isoformat()
        self._events.append(event)

    def list_events(self) -> List[Dict[str, Any]]:
        return list(self._events)
