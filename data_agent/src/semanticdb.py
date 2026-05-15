from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json


@dataclass(frozen=True)
class MetricDef:
    name: str
    aggregation: str
    expression: str
    subject: str


class SemanticDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = {m["name"]: m for m in config.get("metrics", [])}
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

    def metric(self, metric_name: str) -> MetricDef:
        metric = self.metrics[metric_name]
        return MetricDef(
            name=metric["name"],
            aggregation=metric["aggregation"],
            expression=metric["expression"],
            subject=metric["subject"],
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
