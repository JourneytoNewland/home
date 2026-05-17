import unittest

from data_agent.src.auth import AuthorizationError
from data_agent.src.compiler import MySQLCompiler, PostgresCompiler
from data_agent.src.executor import QueryExecutor, AuditLogger, ExecutionError
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.audit_logger = AuditLogger()
        self.pipeline = DataAgentPipeline(self.semantic_db, audit_logger=self.audit_logger)

    def test_deterministic_output(self):
        out1 = self.pipeline.run("今年销售额", role="analyst")
        out2 = self.pipeline.run("今年销售额", role="analyst")
        self.assertEqual(out1["logic_form"], out2["logic_form"])
        self.assertEqual(out1["sql"], out2["sql"])
        self.assertEqual(out1["trace_id"], out2["trace_id"])

    def test_group_by_dimension(self):
        out = self.pipeline.run("今年销售额按省份", role="analyst")
        self.assertIn("GROUP BY province", out["sql"])

    def test_role_row_filter_applied(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        self.assertIn("region in ('East','North')", out["sql"])

    def test_default_deny_permission(self):
        with self.assertRaises(AuthorizationError):
            self.pipeline.run("今年利润", role="analyst")

    def test_mysql_compiler_quotes(self):
        pipeline = DataAgentPipeline(self.semantic_db, compiler=MySQLCompiler())
        out = pipeline.run("今年销售额按省份", role="analyst")
        self.assertIn("`province`", out["sql"])

    def test_postgres_compiler_quotes(self):
        pipeline = DataAgentPipeline(self.semantic_db, compiler=PostgresCompiler())
        out = pipeline.run("今年销售额", role="analyst")
        self.assertIn('"sales_amount"', out["sql"])

    def test_unknown_term_capture(self):
        out = self.pipeline.run("今年GMV销售额", role="analyst")
        self.assertIn("GMV", out["explain"]["unknown_terms"])

    def test_metric_version_selected(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        self.assertEqual(out["explain"]["metric_version"], "v2")
        self.assertIn("sum(order_amount - discount_amount)", out["sql"])

    def test_metric_version_v1_selected_for_early_date(self):
        db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        v1 = db.metric("sales_amount", as_of_date="2026-06-30")
        self.assertEqual(v1.version, "v1")
        self.assertEqual(v1.expression, "order_amount")

    def test_executor_dry_run_mode(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        self.assertEqual(out["execution"]["mode"], "dry_run")
        self.assertEqual(out["execution"]["row_count"], 0)

    def test_readonly_executor_rejects_non_select(self):
        executor = QueryExecutor(mode="sqlite_readonly")
        with self.assertRaises(ExecutionError):
            executor.execute("DELETE FROM dwd_sales_order")

    def test_audit_log_written(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        events = self.audit_logger.list_events()
        self.assertGreaterEqual(len(events), 1)
        self.assertEqual(events[-1]["trace_id"], out["trace_id"])


if __name__ == "__main__":
    unittest.main()
