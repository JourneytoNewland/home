import unittest

from data_agent.src.identity import UserContext


class TestIdentity(unittest.TestCase):
    def test_resolve_requested_role(self):
        ctx = UserContext(user_id="u1", roles=["analyst", "admin"])
        self.assertEqual(ctx.resolve_role("admin"), "admin")

    def test_resolve_active_role(self):
        ctx = UserContext(user_id="u1", roles=["analyst", "admin"], active_role="analyst")
        self.assertEqual(ctx.resolve_role(), "analyst")

    def test_resolve_first_role_fallback(self):
        ctx = UserContext(user_id="u1", roles=["analyst", "admin"])
        self.assertEqual(ctx.resolve_role(), "analyst")

    def test_reject_ungranted_role(self):
        ctx = UserContext(user_id="u1", roles=["analyst"])
        with self.assertRaises(PermissionError):
            ctx.resolve_role("admin")


if __name__ == "__main__":
    unittest.main()
