from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UnknownTermResolver:
    """Stub resolver for unknown terms.

    - vector_map simulates vector retrieval candidates.
    - If unresolved, returns clarify questions for human-in-the-loop.
    """

    vector_map: Dict[str, List[str]]

    def resolve(self, terms: List[str]) -> Dict[str, object]:
        resolved: Dict[str, str] = {}
        unresolved: List[str] = []
        clarifications: List[str] = []

        for term in terms:
            candidates = self.vector_map.get(term.upper(), [])
            if len(candidates) == 1:
                resolved[term] = candidates[0]
            else:
                unresolved.append(term)
                if candidates:
                    clarifications.append(f"术语'{term}'可能指: {', '.join(candidates)}，请确认。")
                else:
                    clarifications.append(f"术语'{term}'未识别，请补充业务定义。")

        return {
            "resolved": resolved,
            "unresolved": unresolved,
            "clarifications": clarifications,
        }
