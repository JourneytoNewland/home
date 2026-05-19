import unittest

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


class TestFinalE2EContractTDD(unittest.TestCase):
    def test_pipeline_to_service_end_to_end_contract(self):
        semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
        logger = AuditLogger(store=AuditStore())
        pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
        service = AuditReplayService(logger)

        out = pipeline.run("今年销售额按省份", role="analyst")
        self.assertIn("trace_id", out)

        replay = service.replay_safe(
            actor="u_admin",
            actor_role="admin",
            scope_to_actor=False,
            sort_by="logged_at",
            sort_order="desc",
            limit=10,
            offset=0,
        )
        self.assertEqual(replay["code"], "OK")
        self.assertTrue(any(item["trace_id"] == out["trace_id"] for item in replay["items"]))


if __name__ == "__main__":
    unittest.main()
