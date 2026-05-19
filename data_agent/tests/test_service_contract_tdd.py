import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService
from data_agent.src.service_schema import validate_audit_service_response
from data_agent.src.errors import DataAgentError


class TestServiceContractTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)
        self.pipeline.run("今年销售额", role="analyst")
        self.service = AuditReplayService(self.logger)

    def test_service_success_contract_valid(self):
        resp = self.service.replay(actor="u1")
        validate_audit_service_response(resp)
        self.assertEqual(resp["code"], "OK")

    def test_service_error_contract_valid(self):
        resp = self.service.replay_safe(actor="u1", sort_by="bad")
        validate_audit_service_response(resp)
        self.assertEqual(resp["code"], "AUDIT_INVALID_QUERY")

    def test_schema_rejects_missing_field(self):
        bad = {"code": "OK"}
        with self.assertRaises(DataAgentError):
            validate_audit_service_response(bad)


if __name__ == "__main__":
    unittest.main()
