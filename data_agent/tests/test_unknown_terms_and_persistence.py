import os
import tempfile
import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.unknown_terms import UnknownTermResolver


class TestUnknownTermsAndPersistence(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")

    def test_unknown_term_resolution_single_candidate(self):
        resolver = UnknownTermResolver(vector_map={"GMV": ["sales_amount"]})
        pipeline = DataAgentPipeline(self.semantic_db, unknown_term_resolver=resolver)
        out = pipeline.run("今年GMV销售额", role="analyst")
        self.assertEqual(out["explain"]["unknown_resolution"]["resolved"]["GMV"], "sales_amount")

    def test_unknown_term_clarification_multiple_candidates(self):
        resolver = UnknownTermResolver(vector_map={"GMV": ["sales_amount", "gross_merchandise_value"]})
        pipeline = DataAgentPipeline(self.semantic_db, unknown_term_resolver=resolver)
        out = pipeline.run("今年GMV销售额", role="analyst")
        self.assertIn("GMV", out["explain"]["unknown_resolution"]["unresolved"])
        self.assertGreaterEqual(len(out["explain"]["unknown_resolution"]["clarifications"]), 1)

    def test_audit_jsonl_persistence_and_reload(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            path = tmp.name
        try:
            store = AuditStore(persist_path=path)
            logger = AuditLogger(store=store)
            pipeline = DataAgentPipeline(self.semantic_db, audit_logger=logger)
            out = pipeline.run("今年销售额", role="analyst")
            self.assertEqual(len(store.all()), 1)

            reloaded = AuditStore(persist_path=path)
            rows = reloaded.query(trace_id=out["trace_id"])
            self.assertEqual(len(rows), 1)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()

class TestAuditReplayPagination(unittest.TestCase):
    def test_replay_limit_offset(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        logger = AuditLogger()
        pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
        pipeline.run("今年销售额", role="analyst")
        pipeline.run("今年销售额按省份", role="analyst")

        first = pipeline.audit_replay(limit=1, offset=0)
        second = pipeline.audit_replay(limit=1, offset=1)
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertNotEqual(first[0]["trace_id"], second[0]["trace_id"])
