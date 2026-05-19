import json
import subprocess
import unittest
from pathlib import Path


class TestOpenApiAndDemoTDD(unittest.TestCase):
    def test_openapi_has_query_and_replay(self):
        spec = json.loads(Path('data_agent/api/openapi.json').read_text(encoding='utf-8'))
        self.assertIn('/query', spec['paths'])
        self.assertIn('/replay', spec['paths'])

    def test_demo_script_runs(self):
        proc = subprocess.run(['python3', 'data_agent/scripts/demo_run.py'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn('[query#1]', proc.stdout)
        self.assertIn('[replay/admin]', proc.stdout)


if __name__ == '__main__':
    unittest.main()
