from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List
import json


@dataclass(frozen=True)
class MetricDef:
    name: str
    aggregation: str
    expression: str
    subject: str
    version: str
    effective_from: str
    effective_to: str | None


class SemanticDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = config.get("metrics", [])
        self.entities = {e["name"]: e for e in config.get("entities", [])}
        self.policies = config.get("policies", {"default_deny": True, "roles": {}})

    @classmethod
    def from_file(cls, path: str) -> "SemanticDB":
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix == ".json":
            return cls(json.loads(p.read_text(encoding="utf-8")))

        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except Exception as exc:
                raise RuntimeError("PyYAML is required to load YAML semantic config.") from exc
            return cls(yaml.safe_load(p.read_text(encoding="utf-8")))

        raise ValueError(f"Unsupported config format: {suffix}")

    @staticmethod
    def _parse_date(value: str) -> date:
        return date.fromisoformat(value)

    def metric(self, metric_name: str, as_of_date: str) -> MetricDef:
        target = self._parse_date(as_of_date)
        candidates = [m for m in self.metrics if m["name"] == metric_name]
        if not candidates:
            raise KeyError(f"Metric not found: {metric_name}")

        matched = []
        for metric in candidates:
            start = self._parse_date(metric["effective_from"])
            end = self._parse_date(metric["effective_to"]) if metric.get("effective_to") else None
            if target >= start and (end is None or target <= end):
                matched.append(metric)

        if not matched:
            raise KeyError(f"Metric {metric_name} has no effective version for {as_of_date}")

        selected = sorted(matched, key=lambda x: x["effective_from"], reverse=True)[0]
        return MetricDef(
            name=selected["name"],
            aggregation=selected["aggregation"],
            expression=selected["expression"],
            subject=selected["subject"],
            version=selected["version"],
            effective_from=selected["effective_from"],
            effective_to=selected.get("effective_to"),
        )

    def table_for_subject(self, subject: str) -> str:
        return self.entities[subject]["table"]

    def role_allowed_metrics(self, role: str) -> List[str]:
        roles = self.policies.get("roles", {})
        role_cfg = roles.get(role, {})
        return role_cfg.get("allowed_metrics", [])

    def role_row_filter(self, role: str) -> str | None:
        roles = self.policies.get("roles", {})
        role_cfg = roles.get(role, {})
        return role_cfg.get("row_filter")

    def default_deny(self) -> bool:
        return bool(self.policies.get("default_deny", True))
