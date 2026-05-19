import os
import tempfile
import unittest

from data_agent.src.audit import AuditStore


class TestAuditAppendRobustnessTDD(unittest.TestCase):
    def test_append_persists_jsonl_line(self):
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp:
            path = tmp.name
        try:
            store = AuditStore(persist_path=path)
            event = {"trace_id": "t1", "role": "analyst"}
            store.append(event)

            with open(path, 'r', encoding='utf-8') as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
            self.assertEqual(len(lines), 1)
            self.assertIn('"trace_id": "t1"', lines[0])
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
