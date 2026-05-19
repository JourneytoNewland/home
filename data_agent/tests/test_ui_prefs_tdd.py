import unittest
from pathlib import Path


class TestUIPrefsTDD(unittest.TestCase):
    def test_ui_contains_localstorage_pref_logic(self):
        html = Path('data_agent/ui/index.html').read_text(encoding='utf-8')
        self.assertIn('localStorage.setItem', html)
        self.assertIn('loadPrefs', html)
        self.assertIn('da_prefs', html)


if __name__ == '__main__':
    unittest.main()
