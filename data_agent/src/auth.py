from data_agent.src.semanticdb import SemanticDB


class AuthorizationError(PermissionError):
    pass


def enforce_metric_access(semantic_db: SemanticDB, role: str, metric_name: str) -> None:
    allowed = semantic_db.role_allowed_metrics(role)
    if metric_name in allowed:
        return

    if semantic_db.default_deny():
        raise AuthorizationError(f"Role '{role}' is not allowed to access metric '{metric_name}'.")
