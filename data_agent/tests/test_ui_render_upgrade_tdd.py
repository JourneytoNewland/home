import unittest
from pathlib import Path


class TestUIRenderUpgradeTDD(unittest.TestCase):
    def test_ui_contains_result_cards_and_replay_list(self):
        html = Path('data_agent/ui/index.html').read_text(encoding='utf-8')
        self.assertIn('resultCards', html)
        self.assertIn('replayList', html)
        self.assertIn('copyText', html)


if __name__ == '__main__':
    unittest.main()
