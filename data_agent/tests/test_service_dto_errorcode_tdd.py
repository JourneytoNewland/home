import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


class TestServiceDtoErrorcodeTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)
        self.pipeline.run("今年销售额", role="analyst")

    def test_service_success_response_has_code_message(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay(actor="u1")
        self.assertEqual(resp["code"], "OK")
        self.assertEqual(resp["message"], "success")

    def test_service_error_response_has_code_message(self):
        svc = AuditReplayService(self.logger)
        resp = svc.replay_safe(actor="u1", sort_by="bad_field")
        self.assertEqual(resp["code"], "AUDIT_INVALID_QUERY")
        self.assertIn("sort_by", resp["message"])
        self.assertEqual(resp["items"], [])


if __name__ == "__main__":
    unittest.main()
