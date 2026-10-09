"""Strict identical-source SHA for original JAN039 selected benchmark."""
import hashlib
import unittest
from pathlib import Path

class FrozenJAN039(unittest.TestCase):
    def test_unmodified_frozen_selected_reference(self):
        path=Path(__file__).with_name('JAN039_SELECTED_VERIFIED.json')
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         '119ca28bd20a61f56771e2b3ab3577f47a362f30e447af71f0c89d38a99704ae')

if __name__ == '__main__':
    unittest.main()
