from dataclasses import dataclass, field
from typing import Dict, List, Any

from data_agent.src.auth import enforce_metric_access
from data_agent.src.compiler import GenericSQLCompiler, with_trace_id
from data_agent.src.semanticdb import SemanticDB


@dataclass(frozen=True)
class QueryObject:
    subject: str
    metric: str
    aggregation: str
    time_field: str
    start_date: str
    end_date: str
    dimensions: List[str] = field(default_factory=list)


class NLStandardizer:
    """Placeholder for LLM-based NL normalization.
    Deterministic mapping for MVP tests.
    """

    @staticmethod
    def normalize(raw_question: str) -> QueryObject:
        text = raw_question.strip()
        if "利润" in text:
            return QueryObject(
                subject="sales_order",
                metric="profit_amount",
                aggregation="sum",
                time_field="order_date",
                start_date="2026-01-01",
                end_date="2026-12-31",
                dimensions=[],
            )
        if "销售额" in text and "按省份" in text:
            return QueryObject(
                subject="sales_order",
                metric="sales_amount",
                aggregation="sum",
                time_field="order_date",
                start_date="2026-01-01",
                end_date="2026-12-31",
                dimensions=["province"],
            )
        return QueryObject(
            subject="sales_order",
            metric="sales_amount",
            aggregation="sum",
            time_field="order_date",
            start_date="2026-01-01",
            end_date="2026-12-31",
            dimensions=[],
        )


class DeterministicReasoner:
    @staticmethod
    def to_logic_form(q: QueryObject) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "subject": q.subject,
            "metric": {"name": q.metric, "aggregation": q.aggregation, "filters": []},
            "dimensions": q.dimensions,
            "time_range": {
                "field": q.time_field,
                "start": q.start_date,
                "end": q.end_date,
            },
        }


class DataAgentPipeline:
    def __init__(self, semantic_db: SemanticDB, compiler: GenericSQLCompiler | None = None):
        self.semantic_db = semantic_db
        self.compiler = compiler or GenericSQLCompiler()

    def run(self, raw_question: str, role: str = "analyst") -> Dict[str, Any]:
        q = NLStandardizer.normalize(raw_question)
        enforce_metric_access(self.semantic_db, role, q.metric)

        lf = DeterministicReasoner.to_logic_form(q)
        metric_def = self.semantic_db.metric(q.metric)
        table = self.semantic_db.table_for_subject(metric_def.subject)
        row_filter = self.semantic_db.role_row_filter(role)

        sql = self.compiler.compile(lf, table, metric_def.expression, row_filter)
        compiled = with_trace_id(sql, lf)
        return {
            "query_object": q,
            "logic_form": lf,
            "trace_id": compiled["trace_id"],
            "sql": compiled["sql"],
        }
