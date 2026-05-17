import unittest

from data_agent.src.auth import AuthorizationError
from data_agent.src.compiler import MySQLCompiler, PostgresCompiler
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.pipeline = DataAgentPipeline(self.semantic_db)

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


if __name__ == "__main__":
    unittest.main()
