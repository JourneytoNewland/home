from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any

from data_agent.src.auth import enforce_metric_access
from data_agent.src.compiler import GenericSQLCompiler, with_trace_id
from data_agent.src.executor import QueryExecutor, AuditLogger
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.validator import validate_logic_form


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
    ):
        self.semantic_db = semantic_db
        self.compiler = compiler or GenericSQLCompiler()
        self.executor = executor or QueryExecutor(mode="dry_run")
        self.audit_logger = audit_logger or AuditLogger()

    def run(self, raw_question: str, role: str = "analyst") -> Dict[str, Any]:
        q = NLStandardizer.normalize(raw_question)
        enforce_metric_access(self.semantic_db, role, q.metric)
        lf = DeterministicReasoner.to_logic_form(q)

        metric_def = self.semantic_db.metric(q.metric, as_of_date=q.end_date)
        table = self.semantic_db.table_for_subject(metric_def.subject)
        row_filter = self.semantic_db.role_row_filter(role)

        sql = self.compiler.compile(lf, table, metric_def.expression, row_filter)
        compiled = with_trace_id(sql, lf)
        execution = self.executor.execute(compiled["sql"])

        event = {
            "trace_id": compiled["trace_id"],
            "role": role,
            "metric": q.metric,
            "metric_version": metric_def.version,
            "sql": compiled["sql"],
            "execution_mode": execution["mode"],
            "row_count": execution["row_count"],
        }
        self.audit_logger.log(event)

        return {
            "query_object": asdict(q),
            "logic_form": lf,
            "trace_id": compiled["trace_id"],
            "sql": compiled["sql"],
            "execution": execution,
            "explain": {
                "metric": q.metric,
                "subject": q.subject,
                "time_range": {"start": q.start_date, "end": q.end_date},
                "role": role,
                "row_filter": row_filter,
                "unknown_terms": q.unknown_terms,
                "metric_version": metric_def.version,
                "metric_effective_from": metric_def.effective_from,
                "metric_effective_to": metric_def.effective_to,
            },
        }
