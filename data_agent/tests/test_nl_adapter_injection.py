import unittest

from data_agent.src.pipeline import DataAgentPipeline, QueryObject
from data_agent.src.semanticdb import SemanticDB


class FakeNLStandardizer:
    def normalize(self, raw_question: str) -> QueryObject:
        # deliberately ignore input to verify adapter injection path
        return QueryObject(
            subject="sales_order",
            metric="sales_amount",
            aggregation="sum",
            time_field="order_date",
            start_date="2026-01-01",
            end_date="2026-12-31",
            dimensions=["province"],
            unknown_terms=[],
        )


class TestNLAdapterInjection(unittest.TestCase):
    def test_pipeline_uses_injected_standardizer(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        pipeline = DataAgentPipeline(semantic_db, nl_standardizer=FakeNLStandardizer())
        out = pipeline.run("totally unrelated question", role="analyst")
        self.assertIn("GROUP BY province", out["sql"])


if __name__ == "__main__":
    unittest.main()
