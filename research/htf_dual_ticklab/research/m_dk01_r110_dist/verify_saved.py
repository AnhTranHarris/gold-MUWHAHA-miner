"""Independent verification of frozen files; does not refit or select thresholds."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'sources/filter08_recovered.zip'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    manifest = json.loads((ROOT / 'models/manifest.json').read_text())
    assert sha(ROOT / 'PLAN.md') == manifest['plan_sha256']
    for model in manifest['models']:
        assert sha(ROOT / 'models' / model['model']) == model['sha256'], model['model']
    contract = json.loads((ROOT / 'SOURCE_CONTRACT.json').read_text())
    for filename, expected in contract['sources'].items():
        assert sha(SOURCE.parent / filename) == expected, filename
    results = json.loads((ROOT / 'results/RESULTS.json').read_text())['rows']
    cutoffs = json.loads((ROOT / 'results/FROZEN_CAL.json').read_text())
    output = []
    with zipfile.ZipFile(SOURCE) as archive:
        for month in ('01', '02', '06', '07'):
            source = np.load(io.BytesIO(archive.read(
                f'FILTER08/FITTED_CLASSIFIER_SCORES_dukascopy_{month}.npz')))
            scores = np.load(ROOT / f'results/scores_{month}.npz')
            masks = np.load(ROOT / f'results/masks_{month}.npz')
            for key in ('t', 'original_side', 'truth_class'):
                np.testing.assert_array_equal(source[key], scores[key])
                np.testing.assert_array_equal(source[key], masks[key])
            np.testing.assert_array_equal(source['kept'], scores['teacher_kept'])
            row = {'month': month, 'events': len(source['t']), 'recount': {}}
            for policy, budgets in cutoffs.items():
                for budget, threshold in budgets.items():
                    mask = masks[policy + '_' + budget]
                    np.testing.assert_array_equal(mask, scores[policy] > threshold)
                    correct = source['truth_class'] == 0
                    wrong, right = int((mask & ~correct).sum()), int((mask & correct).sum())
                    reported = next(r for r in results if r['month'] == month
                        and r['policy'] == policy and r['budget'] == budget
                        and r['split'] in ('FULL_MIXED', 'FULL_EXPOSED'))
                    assert (wrong, right) == (reported['incorrect_veto'], reported['correct_lost'])
                    row['recount'][policy + '_' + budget] = [wrong, right]
            output.append(row)
    print(json.dumps({'status': 'PASS', 'models': len(manifest['models']),
                      'original_events': sum(x['events'] for x in output),
                      'months': output}, indent=2))


if __name__ == '__main__':
    main()
