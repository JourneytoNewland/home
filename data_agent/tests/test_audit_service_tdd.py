import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.identity import UserContext
from data_agent.src.service import AuditReplayService


class TestAuditReplayServiceTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)

        self.pipeline.run("今年销售额", role="analyst")
        admin = UserContext(user_id="u_admin", roles=["analyst", "admin"], active_role="admin")
        self.pipeline.run("今年利润", role=None, user_context=admin)

    def test_replay_response_shape(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(limit=1)
        self.assertIn("items", resp)
        self.assertIn("total", resp)
        self.assertIn("limit", resp)
        self.assertIn("offset", resp)
        self.assertEqual(resp["limit"], 1)

    def test_replay_total_independent_of_limit(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(limit=1)
        self.assertGreaterEqual(resp["total"], 2)
        self.assertEqual(len(resp["items"]), 1)

    def test_replay_next_offset(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(limit=1, offset=0)
        self.assertEqual(resp["next_offset"], 1)


if __name__ == "__main__":
    unittest.main()
