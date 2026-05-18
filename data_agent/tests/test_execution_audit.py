import os
import sqlite3
import tempfile
import unittest

from data_agent.src.executor import QueryExecutor, AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.identity import UserContext


class TestExecutionAndAudit(unittest.TestCase):
    def setUp(self):
        self.semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")

    def test_sqlite_readonly_select_executes(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE dwd_sales_order (order_date TEXT, order_amount REAL, discount_amount REAL, region TEXT, province TEXT)")
            cur.execute("INSERT INTO dwd_sales_order VALUES ('2026-08-01', 100.0, 5.0, 'East', 'ZJ')")
            conn.commit()
            conn.close()

            executor = QueryExecutor(mode="sqlite_readonly", sqlite_path=db_path)
            pipeline = DataAgentPipeline(self.semantic_db, executor=executor, audit_logger=AuditLogger())
            out = pipeline.run("今年销售额", role="analyst")
            self.assertEqual(out["execution"]["mode"], "sqlite_readonly")
            self.assertEqual(out["execution"]["row_count"], 1)
        finally:
            os.remove(db_path)

    def test_audit_replay_filters(self):
        logger = AuditLogger()
        pipeline = DataAgentPipeline(self.semantic_db, audit_logger=logger)
        ctx_admin = UserContext(user_id="u_admin", roles=["analyst", "admin"], active_role="admin")

        out1 = pipeline.run("今年销售额", role="analyst")
        out2 = pipeline.run("今年利润", role=None, user_context=ctx_admin)

        by_trace = pipeline.audit_replay(trace_id=out1["trace_id"])
        self.assertEqual(len(by_trace), 1)

        by_user = pipeline.audit_replay(user_id="u_admin")
        self.assertEqual(len(by_user), 1)
        self.assertEqual(by_user[0]["trace_id"], out2["trace_id"])

        by_role = pipeline.audit_replay(role="analyst")
        self.assertGreaterEqual(len(by_role), 1)

        by_metric = pipeline.audit_replay(metric="profit_amount")
        self.assertEqual(len(by_metric), 1)


if __name__ == "__main__":
    unittest.main()
