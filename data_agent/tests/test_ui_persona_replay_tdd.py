import unittest
from data_agent.ui import server


class TestUIPersonaReplayTDD(unittest.TestCase):
    def test_admin_replay_unmasked(self):
        server.pipeline.run("今年利润", role="admin")
        resp = server.service.replay_safe(actor="u_admin", actor_role="admin", scope_to_actor=False)
        self.assertEqual(resp["code"], "OK")

    def test_analyst_replay_masked(self):
        server.pipeline.run("今年销售额", role="analyst")
        resp = server.service.replay_safe(actor="u_admin", actor_role="analyst", scope_to_actor=False)
        self.assertEqual(resp["code"], "AUDIT_FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
