"""CI fail-closed original FEB042/FEB044/FEB045/FEB047 SOURCE BYTE LOCK.

Large original FEB042 arrays + full raw February ticks remain external and were
independently replayed offline. This CI test does not fake large-data replay.
"""
from pathlib import Path
import hashlib,json,unittest

class FrozenFebruarySourceContract(unittest.TestCase):
    def test_all_seven_verbatim_original_scripts_hash_match(self):
        base=Path(__file__).resolve().parent
        manifest=json.loads((base/'FEB045_SOURCE_GATE_033_MANIFEST.json').read_text())
        self.assertEqual(len(manifest['original_source_sha256']),7)
        for path,digest in manifest['original_source_sha256'].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((base/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(manifest['original_archives_sha256']['FEB045'],
            '9248646bf099b954b5661c765ce50316a61c015b595ad61128a0c02b115a33df')
        self.assertEqual(manifest['original_source_mask']['mismatches'],0)
        self.assertEqual(manifest['original_source_mask']['source_mask_permitted'],34063)
        self.assertEqual(manifest['original_source_mask']['native_permitted'],34063)
        self.assertEqual(manifest['feb_quote_feature_parity']['exact_count_range_mismatches'],0)

if __name__ == '__main__':unittest.main()