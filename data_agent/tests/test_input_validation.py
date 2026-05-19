import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.errors import AuditQueryError, NLAdapterError
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB


class BadNLStandardizer:
    def normalize(self, raw_question: str):
        return {"bad": "payload"}


class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")

    def test_audit_invalid_start_time(self):
        store = AuditStore()
        with self.assertRaises(AuditQueryError):
            store.query(start_time="not-a-time")

    def test_audit_invalid_end_time(self):
        store = AuditStore()
        with self.assertRaises(AuditQueryError):
            store.query(end_time="bad-time")

    def test_audit_negative_offset(self):
        store = AuditStore()
        with self.assertRaises(AuditQueryError):
            store.query(offset=-1)

    def test_audit_negative_limit(self):
        store = AuditStore()
        with self.assertRaises(AuditQueryError):
            store.query(limit=-2)


    def test_audit_invalid_sort_order_param(self):
        store = AuditStore()
        with self.assertRaises(AuditQueryError):
            store.query(sort_order="INVALID")

    def test_nl_adapter_invalid_payload(self):
        pipeline = DataAgentPipeline(self.semantic_db, nl_standardizer=BadNLStandardizer())
        with self.assertRaises(NLAdapterError):
            pipeline.run("今年销售额", role="analyst")


if __name__ == "__main__":
    unittest.main()
