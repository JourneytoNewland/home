from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any

from data_agent.src.auth import enforce_metric_access
from data_agent.src.compiler import GenericSQLCompiler, with_trace_id
from data_agent.src.executor import QueryExecutor, AuditLogger
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.identity import UserContext
from data_agent.src.validator import validate_logic_form
from data_agent.src.unknown_terms import UnknownTermResolver


@dataclass(frozen=True)
class QueryObject:
    subject: str
    metric: str
    aggregation: str
    time_field: str
    start_date: str
    end_date: str
    dimensions: List[str] = field(default_factory=list)
    unknown_terms: List[str] = field(default_factory=list)


class NLStandardizer:
    @staticmethod
    def normalize(raw_question: str) -> QueryObject:
        text = raw_question.strip()
        unknown_terms: List[str] = []
        if "GMV" in text.upper():
            unknown_terms.append("GMV")

        if "利润" in text:
            return QueryObject("sales_order", "profit_amount", "sum", "order_date", "2026-01-01", "2026-12-31", [], unknown_terms)
        if "销售额" in text and "按省份" in text:
            return QueryObject("sales_order", "sales_amount", "sum", "order_date", "2026-01-01", "2026-12-31", ["province"], unknown_terms)
        return QueryObject("sales_order", "sales_amount", "sum", "order_date", "2026-01-01", "2026-12-31", [], unknown_terms)


class DeterministicReasoner:
    @staticmethod
    def to_logic_form(q: QueryObject) -> Dict[str, Any]:
        lf = {
            "version": "1.0",
            "subject": q.subject,
            "metric": {"name": q.metric, "aggregation": q.aggregation, "filters": []},
            "dimensions": q.dimensions,
            "time_range": {"field": q.time_field, "start": q.start_date, "end": q.end_date},
        }
        validate_logic_form(lf)
        return lf


class DataAgentPipeline:
    def __init__(
        self,
        semantic_db: SemanticDB,
        compiler: GenericSQLCompiler | None = None,
        executor: QueryExecutor | None = None,
        audit_logger: AuditLogger | None = None,
        unknown_term_resolver: UnknownTermResolver | None = None,
    ):
        self.semantic_db = semantic_db
        self.compiler = compiler or GenericSQLCompiler()
        self.executor = executor or QueryExecutor(mode="dry_run")
        self.audit_logger = audit_logger or AuditLogger()
        self.unknown_term_resolver = unknown_term_resolver or UnknownTermResolver(vector_map={"GMV": ["sales_amount"]})

    def run(
        self,
        raw_question: str,
        role: str | None = "analyst",
        user_context: UserContext | None = None,
    ) -> Dict[str, Any]:
        q = NLStandardizer.normalize(raw_question)
        resolved_role = user_context.resolve_role(role) if user_context else (role or "analyst")
        enforce_metric_access(self.semantic_db, resolved_role, q.metric)
        lf = DeterministicReasoner.to_logic_form(q)

        unknown_resolution = self.unknown_term_resolver.resolve(q.unknown_terms)

        metric_def = self.semantic_db.metric(q.metric, as_of_date=q.end_date)
        table = self.semantic_db.table_for_subject(metric_def.subject)
        row_filter = self.semantic_db.role_row_filter(resolved_role)

        sql = self.compiler.compile(lf, table, metric_def.expression, row_filter)
        compiled = with_trace_id(sql, lf)
        execution = self.executor.execute(compiled["sql"])

        event = {
            "user_id": user_context.user_id if user_context else None,
            "trace_id": compiled["trace_id"],
            "role": resolved_role,
            "metric": q.metric,
            "metric_version": metric_def.version,
            "sql": compiled["sql"],
            "execution_mode": execution["mode"],
            "row_count": execution["row_count"],
        }
        self.audit_logger.log(event)

        return {
            "user_id": user_context.user_id if user_context else None,
            "query_object": asdict(q),
            "logic_form": lf,
            "trace_id": compiled["trace_id"],
            "sql": compiled["sql"],
            "execution": execution,
            "explain": {
                "metric": q.metric,
                "subject": q.subject,
                "time_range": {"start": q.start_date, "end": q.end_date},
                "role": resolved_role,
                "row_filter": row_filter,
                "unknown_terms": q.unknown_terms,
                "unknown_resolution": unknown_resolution,
                "metric_version": metric_def.version,
                "metric_effective_from": metric_def.effective_from,
                "metric_effective_to": metric_def.effective_to,
            },
        }


    def audit_events(self) -> List[Dict[str, Any]]:
        return self.audit_logger.list_events()

    def audit_replay(
        self,
        trace_id: str | None = None,
        user_id: str | None = None,
        role: str | None = None,
        metric: str | None = None,
    ) -> List[Dict[str, Any]]:
        return self.audit_logger.replay(trace_id=trace_id, user_id=user_id, role=role, metric=metric)
