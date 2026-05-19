from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from data_agent.src.errors import NLAdapterError


class NLClient(Protocol):
    def normalize(self, text: str) -> Dict[str, Any]:
        ...


@dataclass
class ExternalNLAdapter:
    """Adapter that wraps an external NL normalization client.

    Expected payload keys:
    subject, metric, aggregation, time_field, start_date, end_date,
    dimensions (list), unknown_terms (list)
    """

    client: NLClient
    query_object_cls: type

    def normalize(self, raw_question: str):
        payload = self.client.normalize(raw_question)
        required = [
            "subject",
            "metric",
            "aggregation",
            "time_field",
            "start_date",
            "end_date",
            "dimensions",
            "unknown_terms",
        ]
        for k in required:
            if k not in payload:
                raise NLAdapterError(f"external NL payload missing key: {k}")

        if not isinstance(payload["dimensions"], list) or not isinstance(payload["unknown_terms"], list):
            raise NLAdapterError("external NL payload has invalid list fields")

        return self.query_object_cls(
            payload["subject"],
            payload["metric"],
            payload["aggregation"],
            payload["time_field"],
            payload["start_date"],
            payload["end_date"],
            payload["dimensions"],
            payload["unknown_terms"],
        )
