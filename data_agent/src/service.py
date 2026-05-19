from __future__ import annotations

from typing import Any, Dict, Protocol

from data_agent.src.errors import DataAgentError
from data_agent.src.executor import AuditLogger
from data_agent.src.service_schema import validate_audit_service_response


class AuthzPolicy(Protocol):
    def authorize(self, actor: str | None) -> None:
        ...


class AllowAllPolicy:
    def authorize(self, actor: str | None) -> None:
        return None


class AuditReplayService:
    ALLOWED_SORT_BY = {"logged_at"}

    def __init__(self, audit_logger: AuditLogger, authz_policy: AuthzPolicy | None = None):
        self.audit_logger = audit_logger
        self.authz_policy = authz_policy or AllowAllPolicy()

    @staticmethod
    def _mask_row(row: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(row)
        payload["sql"] = "***MASKED***"
        return payload

    def replay(self, actor: str | None = None, **filters: Any) -> Dict[str, Any]:
        self.authz_policy.authorize(actor)

        actor_role = filters.pop("actor_role", None)
        sort_by = filters.get("sort_by", "logged_at")
        sort_order = filters.get("sort_order", "desc")
        if sort_by not in self.ALLOWED_SORT_BY:
            raise DataAgentError(f"sort_by '{sort_by}' is not allowed")
        if sort_order not in {"asc", "desc"}:
            raise DataAgentError(f"sort_order '{sort_order}' is not allowed")

        scope_to_actor = filters.pop("scope_to_actor", True)
        if scope_to_actor is False and actor is not None and actor_role is not None and actor_role != "admin":
            raise DataAgentError("forbidden: non-admin cannot disable actor scope")

        limit = filters.get("limit")
        offset = filters.get("offset", 0)

        query_filters = dict(filters)
        query_filters.pop("limit", None)
        query_filters.pop("offset", None)

        if scope_to_actor and actor is not None:
            query_filters["user_id"] = actor

        all_items = self.audit_logger.replay(**query_filters)
        total = len(all_items)
        items = self.audit_logger.replay(limit=limit, offset=offset, **query_filters)

        if actor_role == "admin":
            visible_items = items
        else:
            visible_items = [self._mask_row(r) for r in items]

        next_offset = None
        if limit is not None and offset + len(visible_items) < total:
            next_offset = offset + len(visible_items)

        resp = {
            "code": "OK",
            "message": "success",
            "items": visible_items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "next_offset": next_offset,
        }
        validate_audit_service_response(resp)
        return resp

    def replay_safe(self, actor: str | None = None, **filters: Any) -> Dict[str, Any]:
        try:
            return self.replay(actor=actor, **filters)
        except DataAgentError as exc:
            code = "AUDIT_FORBIDDEN" if "forbidden" in str(exc).lower() else "AUDIT_INVALID_QUERY"
            resp = {
                "code": code,
                "message": str(exc),
                "items": [],
                "total": 0,
                "limit": filters.get("limit"),
                "offset": filters.get("offset", 0),
                "next_offset": None,
            }
            validate_audit_service_response(resp)
            return resp
