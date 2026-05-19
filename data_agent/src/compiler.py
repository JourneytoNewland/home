from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Protocol
import hashlib


class DialectCompiler(Protocol):
    def compile(self, logic_form: Dict[str, Any], table: str, metric_expr: str, row_filter: str | None) -> str:
        ...


@dataclass
class GenericSQLCompiler:
    quote_char: str = ""

    def _q(self, identifier: str) -> str:
        if not self.quote_char:
            return identifier
        return f"{self.quote_char}{identifier}{self.quote_char}"

    def compile(self, logic_form: Dict[str, Any], table: str, metric_expr: str, row_filter: str | None) -> str:
        agg = logic_form["metric"]["aggregation"]
        metric = logic_form["metric"]["name"]
        dims = logic_form.get("dimensions", [])
        time_field = logic_form["time_range"]["field"]
        start = logic_form["time_range"]["start"]
        end = logic_form["time_range"]["end"]

        select_dims = ", ".join(self._q(d) for d in dims)
        select_metric = f"{agg}({metric_expr}) AS {self._q(metric)}"

        if select_dims:
            select_clause = f"SELECT {select_dims}, {select_metric}"
            group_clause = f" GROUP BY {select_dims}"
        else:
            select_clause = f"SELECT {select_metric}"
            group_clause = ""

        where_parts = [f"{self._q(time_field)} >= '{start}'", f"{self._q(time_field)} <= '{end}'"]
        if row_filter:
            where_parts.append(f"({row_filter})")

        where_clause = " AND ".join(where_parts)
        return f"{select_clause} FROM {self._q(table)} WHERE {where_clause}{group_clause}"


class MySQLCompiler(GenericSQLCompiler):
    def __init__(self):
        super().__init__(quote_char="`")


class PostgresCompiler(GenericSQLCompiler):
    def __init__(self):
        super().__init__(quote_char='"')


def with_trace_id(sql: str, logic_form: Dict[str, Any]) -> Dict[str, str]:
    trace_id = hashlib.md5(str(logic_form).encode()).hexdigest()[:16]
    return {"trace_id": trace_id, "sql": sql}
