import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.identity import UserContext
from data_agent.src.service import AuditReplayService


class TestAuditServiceScopeMaskTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)

        self.pipeline.run("今年销售额", role="analyst")
        admin = UserContext(user_id="u_admin", roles=["analyst", "admin"], active_role="admin")
        self.pipeline.run("今年利润", role=None, user_context=admin)

    def test_actor_scope_default_filters_to_actor_user_id(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(actor="u_admin")
        self.assertEqual(resp["total"], 1)
        self.assertEqual(resp["items"][0]["user_id"], "u_admin")

    def test_admin_can_disable_scope_filter(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(actor="u_admin", scope_to_actor=False)
        self.assertGreaterEqual(resp["total"], 2)

    def test_mask_sql_for_non_admin(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(actor="u_admin", role="analyst", scope_to_actor=False)
        # analyst role rows should mask sql text
        analyst_rows = [r for r in resp["items"] if r["role"] == "analyst"]
        self.assertTrue(all(r["sql"] == "***MASKED***" for r in analyst_rows))


if __name__ == "__main__":
    unittest.main()
