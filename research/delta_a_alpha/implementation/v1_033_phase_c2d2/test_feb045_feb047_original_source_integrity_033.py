"""FEB045/FEB047 source bytes & immutable strict selected parameters, not prose authority."""
import hashlib
import json
import unittest
from pathlib import Path
from feb045_physical_heat_feb047_queue_033 import StrictQueue047

class FrozenOriginalTests(unittest.TestCase):
    def test_selected_original_executable_sources_are_byte_identical(self):
        here=Path(__file__).parent
        m=json.loads((here/'C2D3H_FEB045_FEB047_ORIGINAL_SOURCE_MANIFEST.json').read_text())
        for name,e in m['complete_original_source_hashes'].items():
            f=here/'verified_original_sources'/name
            with self.subTest(name=name):
                self.assertEqual(f.stat().st_size,e['bytes'])
                self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),e['sha256'])

    def test_strict_selected_parameters_are_exact_and_month_blind(self):
        root=Path(__file__).parent
        x=json.loads((root/'verified_original_sources'/'FEB047'/'FEB047_STRICT_BEST.json').read_text())['params']
        c=StrictQueue047()
        expected=dict(retreat_usd=c.retreat_usd,window_samples=c.window_samples,
                      min_profit=c.min_profit_usd,close_batch=c.close_batch,
                      cooldown_seconds=c.cooldown_seconds,side_limit=c.side_limit,
                      source_only=c.source_only,require_dd=c.require_dd_usd)
        self.assertEqual(x,expected)
        self.assertFalse(any('month' in k.lower() or 'date' in k.lower() for k in x))

if __name__=='__main__':unittest.main()