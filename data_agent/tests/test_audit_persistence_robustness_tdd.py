import os
import tempfile
import unittest

from data_agent.src.audit import AuditStore


class TestAuditPersistenceRobustnessTDD(unittest.TestCase):
    def test_load_jsonl_skips_corrupted_lines(self):
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp:
            path = tmp.name
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('{"trace_id":"ok1","role":"analyst"}\n')
                f.write('not-json\n')
                f.write('{"trace_id":"ok2","role":"admin"}\n')

            store = AuditStore(persist_path=path)
            rows = store.all()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['trace_id'], 'ok1')
            self.assertEqual(rows[1]['trace_id'], 'ok2')
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
