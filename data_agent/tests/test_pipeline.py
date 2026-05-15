import unittest

from data_agent.src.auth import AuthorizationError
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.pipeline = DataAgentPipeline(self.semantic_db)

    def test_deterministic_output(self):
        q = "今年销售额"
        out1 = self.pipeline.run(q, role="analyst")
        out2 = self.pipeline.run(q, role="analyst")
        self.assertEqual(out1["logic_form"], out2["logic_form"])
        self.assertEqual(out1["sql"], out2["sql"])
        self.assertEqual(out1["trace_id"], out2["trace_id"])

    def test_group_by_dimension(self):
        out = self.pipeline.run("今年销售额按省份", role="analyst")
        self.assertIn("GROUP BY province", out["sql"])
        self.assertIn("sum(order_amount)", out["sql"])

    def test_role_row_filter_applied(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        self.assertIn("region in ('East','North')", out["sql"])

    def test_default_deny_permission(self):
        with self.assertRaises(AuthorizationError):
            self.pipeline.run("今年利润", role="analyst")


if __name__ == "__main__":
    unittest.main()
