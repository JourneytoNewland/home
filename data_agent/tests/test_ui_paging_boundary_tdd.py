import unittest
from pathlib import Path


class TestUIPagingBoundaryTDD(unittest.TestCase):
    def test_ui_contains_page_info_and_boundary_controls(self):
        html = Path('data_agent/ui/index.html').read_text(encoding='utf-8')
        self.assertIn('pageInfo', html)
        self.assertIn('btnPrev', html)
        self.assertIn('btnNext', html)
        self.assertIn('replayNextOffset', html)


if __name__ == '__main__':
    unittest.main()
