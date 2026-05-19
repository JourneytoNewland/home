import unittest
from pathlib import Path


class TestUITraceFilterTDD(unittest.TestCase):
    def test_ui_contains_trace_filter_and_detail_panel(self):
        html = Path('data_agent/ui/index.html').read_text(encoding='utf-8')
        self.assertIn('traceFilter', html)
        self.assertIn('detailPanel', html)
        self.assertIn('showDetail', html)


if __name__ == '__main__':
    unittest.main()
