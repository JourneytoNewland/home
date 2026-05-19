import unittest

from data_agent.src.errors import NLAdapterError
from data_agent.src.nl_adapter_external import ExternalNLAdapter
from data_agent.src.pipeline import DataAgentPipeline, NLStandardizer, QueryObject
from data_agent.src.semanticdb import SemanticDB


class GoodClient:
    def normalize(self, text: str):
        return {
            "subject": "sales_order",
            "metric": "sales_amount",
            "aggregation": "sum",
            "time_field": "order_date",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "dimensions": ["province"],
            "unknown_terms": [],
        }


class BadClientMissing:
    def normalize(self, text: str):
        return {"subject": "sales_order"}


class TestExternalNLAdapterTDD(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")

    def test_external_adapter_success(self):
        adapter = ExternalNLAdapter(GoodClient(), QueryObject)
        pipeline = DataAgentPipeline(self.semantic_db, nl_standardizer=NLStandardizer(adapter))
        out = pipeline.run("irrelevant", role="analyst")
        self.assertIn("GROUP BY province", out["sql"])

    def test_external_adapter_missing_key(self):
        adapter = ExternalNLAdapter(BadClientMissing(), QueryObject)
        with self.assertRaises(NLAdapterError):
            adapter.normalize("x")


if __name__ == "__main__":
    unittest.main()
