import unittest
from pathlib import Path


class TestUIPaginationTDD(unittest.TestCase):
    def test_ui_contains_pagination_and_filter_summary(self):
        html = Path('data_agent/ui/index.html').read_text(encoding='utf-8')
        self.assertIn('filterSummary', html)
        self.assertIn('nextPage', html)
        self.assertIn('prevPage', html)
        self.assertIn('offset', html)


if __name__ == '__main__':
    unittest.main()
