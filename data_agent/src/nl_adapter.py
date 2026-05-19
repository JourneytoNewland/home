from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


class NLAdapter(Protocol):
    def normalize(self, raw_question: str) -> Any:
        ...


@dataclass
class RuleBasedNLAdapter:
    """Default local adapter to keep deterministic behavior."""

    query_object_cls: type

    def normalize(self, raw_question: str):
        text = raw_question.strip()
        unknown_terms = []
        if "GMV" in text.upper():
            unknown_terms.append("GMV")

        if "利润" in text:
            return self.query_object_cls("sales_order", "profit_amount", "sum", "order_date", "2026-01-01", "2026-12-31", [], unknown_terms)
        if "销售额" in text and "按省份" in text:
            return self.query_object_cls("sales_order", "sales_amount", "sum", "order_date", "2026-01-01", "2026-12-31", ["province"], unknown_terms)
        return self.query_object_cls("sales_order", "sales_amount", "sum", "order_date", "2026-01-01", "2026-12-31", [], unknown_terms)
