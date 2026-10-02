from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path


def atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2) + '\n')
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache-root', type=Path, required=True)
    ap.add_argument('--lab-dir', type=Path, required=True)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    sys.path.insert(0, str(a.lab_dir))
    import dukas_tick_lab as lab

    months = {}
    for m in range(1, 8):
        meta, t, ask, bid = lab.load(a.cache_root, m)
        s = lab.spec(m)
        q = lab.qa(a.cache_root, m)
        extra = {
            'meta_source_sha256': meta.get('source_sha256') == s['sha256'],
            'meta_source_size': meta.get('source_size_bytes') == s['bytes'],
            'meta_row_count': meta.get('row_count') == s['ticks'],
            'lab_version': meta.get('lab_version') == lab.LAB_VERSION,
            'price_scale': meta.get('price_scale') == lab.PRICE_SCALE,
            'array_lengths': len(t) == len(ask) == len(bid) == s['ticks'],
        }
        checks = {**q['checks'], **extra}
        months[str(m)] = {'pass': all(checks.values()), 'checks': checks}

    out = {
        'schema': 'delta-002-rebuild-qa-v1',
        'status': 'PASS' if all(x['pass'] for x in months.values()) else 'FAIL',
        'months': months,
        'august_accessed': False,
    }
    if a.output:
        atomic(a.output, out)
    print(json.dumps(out, indent=2))
    return 0 if out['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
