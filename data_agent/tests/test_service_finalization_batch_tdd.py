import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


class TestServiceFinalizationBatchTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
        self.pipeline.run("今年销售额", role="analyst")
        self.pipeline.run("今年销售额按省份", role="analyst")
        self.service = AuditReplayService(logger)

    def test_non_admin_cannot_disable_scope(self):
        resp = self.service.replay_safe(actor="u_analyst", actor_role="analyst", scope_to_actor=False)
        self.assertEqual(resp["code"], "AUDIT_FORBIDDEN")

    def test_non_admin_always_masked(self):
        resp = self.service.replay(actor="u_analyst", actor_role="analyst")
        self.assertTrue(all(item["sql"] == "***MASKED***" for item in resp["items"]))

    def test_admin_can_view_unmasked(self):
        resp = self.service.replay(actor="u_admin", actor_role="admin", scope_to_actor=False)
        self.assertTrue(any(item["sql"] != "***MASKED***" for item in resp["items"]))

    def test_safe_replay_handles_forbidden(self):
        resp = self.service.replay_safe(actor="u", actor_role="analyst", sort_by="logged_at", scope_to_actor=False)
        self.assertEqual(resp["code"], "AUDIT_FORBIDDEN")
        self.assertEqual(resp["items"], [])


if __name__ == "__main__":
    unittest.main()
