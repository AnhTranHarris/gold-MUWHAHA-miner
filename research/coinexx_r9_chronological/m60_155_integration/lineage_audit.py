"""Source-exact lineage and checkpoint audit for archived 155-feature R9 LightGBM.

Only the original 1.7 MB approved model ZIP is read; no raw Coinexx ticks,
features, archives or models are regenerated. Model payloads are byte-verified
BEFORE deserialization. No claims of prospective out-of-sample profitability.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
PINS = {
    "hft.py": "dd475c621a47c7d6eecbcb0454976110cb141f20",
    "event_engine.py": "f151abed6abb5f68328f5b451fd5c772abdb5de6",
    "signal_features.py": "5c6710e6b8b1a1c60486e4413de20c82a3c8dfc5",
}
MODEL_SHA = {
    "direct_test_05_shadow.joblib": "48c3e3898aab1a78cc5f3b0fec45137af23f2267a4ef665a73eb1e1c431ed661",
    "direct_test_06_shadow.joblib": "bdeb8c4ccc8b6523c3c2cf1185104162c5bf2e3f45271c42c521e50e660ec121",
    "direct_test_07_shadow.joblib": "bd4c886a470cecac663f5cb71889f195148fa2ef3da932cfce02c361c873e1c5",
    "direct_test_08_shadow.joblib": "b23e84ed6d9d34b68e5496c71304b76c5db8be8b81be85975ea5dcd1f4df830f",
    "direct_test_09_shadow.joblib": "8d6bb3c41741a2223494a8ec87314e9e8d7ea93634ab83498dd133fe7a187d06",
    "direct_all_JanSep_IS_ONLY.joblib": "09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f",
}
CONTRACT_COUNTS = {
    "r9_context": 14, "hft_selected": 25,
    "event_time": 77, "cusum_and_quote_intensity": 23,
    "brownian_geometry": 11, "action_metadata": 5,
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode()
                        + b"\0" + data).hexdigest()


def verify_local_lineage() -> dict:
    actual = {}
    for name, wanted in PINS.items():
        raw = (ROOT/"lineage"/name).read_bytes()
        got = git_blob_sha(raw)
        if got != wanted:
            raise ValueError(f"Original unmodified source pin mismatch: {name}")
        actual[name] = got
    # These imports are of the exact original research formula sources, not
    # inferred indicator proxies or freshly reparameterized versions.
    sys.path.insert(0,str(ROOT/"lineage"))
    from event_engine import FEATURE_NAMES as EVENT_NAMES
    from signal_features import FEATURE_NAMES as QUOTE_NAMES, ACTION_NAMES
    from hft import WINDOWS as HFT_WINDOWS
    import frozen_snapshot
    if (len(EVENT_NAMES) != 77 or len(QUOTE_NAMES) != 23 or
        len(ACTION_NAMES) != 11 or len(HFT_WINDOWS) != 7 or
        len(frozen_snapshot.OLD_HFT_IDX) != 25):
        raise AssertionError("Archived lineage feature dimensions changed")
    if sum(CONTRACT_COUNTS.values()) != 155:
        raise AssertionError("Approved 155-feature schema is incomplete")
    return dict(original_source_git_blobs=actual,
                feature_contract=CONTRACT_COUNTS,model_input_dimensions=155)


def verify_archive(path: Path) -> dict:
    import joblib  # deserialize ONLY after trusted hash pins have been checked
    import numpy as np
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"Corrupt model archive ZIP: {bad}")
        manifest = json.loads(z.read("MANIFEST.json"))
        run = z.read("run_train.py")
        if hashlib.sha256(run).hexdigest() != manifest["paths"]["run_train.py"]:
            raise ValueError("Saved training source does not match its archive receipt")
        priority = z.read("frozen_priority/src/signal_features.py")
        if hashlib.sha256(priority).hexdigest() != (
            "30ef24f0d8aea3dc21fcd13fec434cee86e80bac9783c454bc95c43be642096c"
        ):
            raise ValueError("Original Brownian/quote-intensity source altered")
        if z.read("frozen_competing/src/event_engine.py") != (
                ROOT/"lineage"/"event_engine.py").read_bytes():
            raise ValueError("Archived event-time features differ from repo pin")
        if priority != (ROOT/"lineage"/"signal_features.py").read_bytes():
            raise ValueError("Archived quote-state/analytic features differ from repo pin")
        text = run.decode()
        for expression in (
            "list(range(14))",
            "earlier.OLD_HFT_IDX.tolist()",
            "range(145,145+len(ev['feature_names']))",
            "action_barrier_features(E,meta[:,4],meta[:,2],meta[:,3],side)",
            "meta=np.stack([side,(side==side0).astype('f4')",
            "np.concatenate([np.repeat(b,2,axis=0),np.repeat(new['features'],2,axis=0),analytical,meta]",
        ):
            if expression not in text:
                raise ValueError("Frozen 155-feature training feature order differs")
        model_result = {}
        for name, expected in MODEL_SHA.items():
            raw = z.read("models/"+name)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected:
                raise ValueError(f"Original model digest mismatch: {name}")
            model = joblib.load(io.BytesIO(raw))["model"]
            if (model.n_features_in_ != 155 or model.n_estimators != 95 or
                model.classes_.tolist() != [0,1]):
                raise ValueError(f"Model architecture/class mapping mismatch: {name}")
            model_result[name] = digest
        all_fit = json.loads(z.read("outputs/all_nine_training_receipt.json"))
        if (all_fit["n_features"]!=155 or all_fit["n_entries"]!=303934 or
            all_fit["n_actions"]!=607868):
            raise ValueError("Frozen model training universe changed")
        return dict(model_sha256=model_result,
                    training_source_sha256=hashlib.sha256(run).hexdigest(),
                    frozen_original_r9_opportunities=all_fit["n_entries"],
                    full_fit_status="IN_SAMPLE_ONLY_NOT_TRADING_CERTIFIED")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path,
                        help="Existing unmodified 155-feature Drive ZIP; no download or rebuild")
    a = parser.parse_args()
    result = verify_local_lineage()
    if a.archive:
        result.update(verify_archive(a.archive))
    else:
        result["archive_verification"] = "SKIPPED_NEEDS_USER_PINNED_ZIP"
    result["conclusion"] = "EXACT_FEATURE_LINEAGE_PASS_DOES_NOT_CERTIFY_LIVE_SCORE_PARITY_OR_PNL"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
