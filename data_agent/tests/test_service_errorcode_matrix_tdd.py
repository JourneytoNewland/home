import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


class TestServiceErrorCodeMatrixTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
        self.pipeline.run("今年销售额", role="analyst")
        self.service = AuditReplayService(logger)

    def test_error_code_for_invalid_sort(self):
        resp = self.service.replay_safe(actor="u1", actor_role="admin", sort_by="bad")
        self.assertEqual(resp["code"], "AUDIT_INVALID_QUERY")

    def test_error_code_for_forbidden_scope_disable(self):
        resp = self.service.replay_safe(actor="u1", actor_role="analyst", scope_to_actor=False)
        self.assertEqual(resp["code"], "AUDIT_FORBIDDEN")

    def test_error_code_for_invalid_sort_order(self):
        resp = self.service.replay_safe(actor="u1", actor_role="admin", sort_order="BAD")
        self.assertEqual(resp["code"], "AUDIT_INVALID_QUERY")


if __name__ == "__main__":
    unittest.main()
