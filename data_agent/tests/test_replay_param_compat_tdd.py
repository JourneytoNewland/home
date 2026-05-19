import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


class TestReplayParamCompatTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
        self.pipeline.run("今年销售额", role="analyst")
        self.pipeline.run("今年销售额按省份", role="analyst")
        self.service = AuditReplayService(logger)

    def test_combined_filters_with_pagination(self):
        resp = self.service.replay_safe(
            actor="u1",
            actor_role="admin",
            scope_to_actor=False,
            role="analyst",
            metric="sales_amount",
            sort_by="logged_at",
            sort_order="desc",
            limit=1,
            offset=0,
        )
        self.assertEqual(resp["code"], "OK")
        self.assertEqual(resp["limit"], 1)
        self.assertEqual(len(resp["items"]), 1)

    def test_scope_to_actor_with_missing_actor_is_global(self):
        resp = self.service.replay_safe(actor=None, scope_to_actor=True)
        self.assertEqual(resp["code"], "OK")
        self.assertGreaterEqual(resp["total"], 2)


if __name__ == "__main__":
    unittest.main()
