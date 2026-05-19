import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService
from data_agent.src.service_schema import validate_audit_service_response


class TestPipelineServiceIntegrationTDD(unittest.TestCase):
    def setUp(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        self.logger = AuditLogger(store=AuditStore())
        self.pipeline = DataAgentPipeline(semantic_db, audit_logger=self.logger)
        self.service = AuditReplayService(self.logger)

    def test_pipeline_event_visible_in_service_replay(self):
        out = self.pipeline.run("今年销售额", role="analyst")
        resp = self.service.replay(actor=None, scope_to_actor=False)
        validate_audit_service_response(resp)
        ids = {i["trace_id"] for i in resp["items"]}
        self.assertIn(out["trace_id"], ids)

    def test_pipeline_service_masking_contract(self):
        self.pipeline.run("今年销售额", role="analyst")
        resp = self.service.replay(actor=None, scope_to_actor=False)
        validate_audit_service_response(resp)
        for row in resp["items"]:
            if row.get("role") != "admin":
                self.assertEqual(row["sql"], "***MASKED***")


if __name__ == "__main__":
    unittest.main()
