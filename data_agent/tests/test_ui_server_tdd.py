import unittest
from data_agent.ui import server


class TestUIServerTDD(unittest.TestCase):
    def test_pipeline_query_returns_trace(self):
        out = server.pipeline.run("今年销售额", role="analyst")
        self.assertIn("trace_id", out)

    def test_replay_service_ok(self):
        server.pipeline.run("今年销售额", role="analyst")
        resp = server.service.replay_safe(actor="u_admin", actor_role="admin", scope_to_actor=False)
        self.assertEqual(resp["code"], "OK")


if __name__ == "__main__":
    unittest.main()
