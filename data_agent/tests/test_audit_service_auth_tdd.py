import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService
from data_agent.src.errors import DataAgentError


class DenyPolicy:
    def authorize(self, actor: str | None) -> None:
        raise DataAgentError("forbidden")


class AllowPolicy:
    def authorize(self, actor: str | None) -> None:
        return None


class TestAuditReplayServiceAuthTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)
        self.pipeline.run("今年销售额", role="analyst")

    def test_service_authorization_denied(self):
        svc = AuditReplayService(self.logger, authz_policy=DenyPolicy())
        with self.assertRaises(DataAgentError):
            svc.replay(actor="u1")

    def test_service_authorization_allowed(self):
        svc = AuditReplayService(self.logger, authz_policy=AllowPolicy())
        resp = svc.replay(actor="u1")
        self.assertIn("items", resp)

    def test_service_sort_whitelist_rejects_invalid_sort_by(self):
        svc = AuditReplayService(self.logger, authz_policy=AllowPolicy())
        with self.assertRaises(DataAgentError):
            svc.replay(actor="u1", sort_by="sql")


if __name__ == "__main__":
    unittest.main()
