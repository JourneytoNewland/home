from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class UserContext:
    user_id: str
    roles: List[str]
    active_role: str | None = None

    def resolve_role(self, requested_role: str | None = None) -> str:
        if requested_role:
            if requested_role not in self.roles:
                raise PermissionError(f"User {self.user_id} cannot assume role '{requested_role}'.")
            return requested_role

        if self.active_role:
            if self.active_role not in self.roles:
                raise PermissionError(f"Active role '{self.active_role}' is not granted to user {self.user_id}.")
            return self.active_role

        if not self.roles:
            raise PermissionError(f"User {self.user_id} has no roles.")

        return self.roles[0]
