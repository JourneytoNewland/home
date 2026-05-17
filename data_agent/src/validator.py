from __future__ import annotations

from typing import Any, Dict


def validate_logic_form(logic_form: Dict[str, Any]) -> None:
    required = ["version", "subject", "metric", "time_range"]
    for k in required:
        if k not in logic_form:
            raise ValueError(f"LogicForm missing required field: {k}")

    metric = logic_form["metric"]
    for mk in ["name", "aggregation"]:
        if mk not in metric:
            raise ValueError(f"LogicForm.metric missing required field: {mk}")

    tr = logic_form["time_range"]
    for tk in ["field", "start", "end"]:
        if tk not in tr:
            raise ValueError(f"LogicForm.time_range missing required field: {tk}")
