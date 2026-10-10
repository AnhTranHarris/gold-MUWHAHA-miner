"""Immutable full original source and independently captured original offer parity."""
import hashlib,json,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
PINS={
 'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json':'643103c0c1a260e7ca9a1a9b2c8653c8afcaea5eba513c605a3aca05cbfecb4d',
 'verified_original_sources/FEB042/prepare.py':'fb3cc7831110d6e19b66bd4d2571e7c3609065e2d671eadf446c77f7020cdb41'}
class FrozenSource(unittest.TestCase):
 def test_full_source_byte_sha256(self):
  for path,digest in PINS.items():
   with self.subTest(file=path):self.assertEqual(hashlib.sha256((BASE/path).read_bytes()).hexdigest(),digest)
 def test_raw_full_quote_entry_replay_is_exact_and_economically_unclaimed(self):
  d=json.loads((BASE/'JAN038_FEB042_ONLINE_FULL_EVENT_PARITY.json').read_text())
  self.assertEqual(d['tape_quotes'],11439219)
  self.assertEqual(d['original_offers'],234698)
  self.assertEqual(d['mismatch'],dict(phase=0,spread=0,imp20=0,excluded=0))
  self.assertTrue(d['does_not_certify_upstream_source_generator_or_funded_pnl'])
 def test_source_ablation_does_not_replace_original_parameter(self):
  d=json.loads((BASE/'FEB042_SOURCE_FEATURE_ABLATIONS.json').read_text())
  self.assertEqual(d['variants']['window_20000_left']['mismatches'],0)
  for name,result in d['variants'].items():
   if name!='window_20000_left':self.assertGreater(result['mismatches'],0)
if __name__=='__main__':unittest.main()
