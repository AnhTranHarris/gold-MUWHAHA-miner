#!/usr/bin/env python3
"""BETA GOV-001 rebuild-artifact durability gate.

This guard prevents CURRENT_STATE from advancing beyond the BETA064 R18 recovery
closure unless the new durable scientific unit points to a complete rebuild
manifest.

It does not prove scientific validity or MT5 approval. It proves that the
project preserved enough declared source/provenance to avoid another
"checkpoint exists but its helper disappeared" failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "CURRENT_STATE.json"
POLICY = ROOT / "research/governance/BETA_GOV_001_MT5_REBUILD_ARTIFACT_RETENTION_POLICY.md"
TEMPLATE = ROOT / "research/artifacts/BETA_RESEARCH_UNIT_REBUILD_MANIFEST_TEMPLATE.json"

R18_BASELINE = "BETA_064_MULTIDESK_LOOP_RECOVERY_R18_STATE_MACHINE_TOPOLOGY_FINAL"

REQUIRED_MANIFEST_KEYS = {
    "schema",
    "unit_id",
    "status",
    "python_rebuild_ready",
    "mt5_translation_ready",
    "missing_required_artifacts",
    "source_code",
    "helpers",
    "inputs",
    "intermediate_surfaces",
    "models",
    "outputs",
    "qa",
    "reconstruction",
    "github_commits",
    "drive_artifacts",
    "verification",
}

REQUIRED_RECONSTRUCTION_KEYS = {
    "entry_point",
    "command",
    "required_artifact_order",
    "expected_fingerprints",
    "timing_semantics",
    "notes",
}


def fail(msg: str) -> None:
    print(f"BETA_GOV_001 FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    if not POLICY.exists():
        fail(f"missing governance policy: {POLICY.relative_to(ROOT)}")
    if not TEMPLATE.exists():
        fail(f"missing rebuild manifest template: {TEMPLATE.relative_to(ROOT)}")

    state = load_json(CURRENT)
    gov = state.get("mt5_rebuild_artifact_retention")
    if not isinstance(gov, dict) or gov.get("status") != "MANDATORY_ACTIVE":
        fail("CURRENT_STATE does not have active BETA GOV-001 retention policy")

    current_unit = state.get("last_verified_durable_unit")
    if current_unit == R18_BASELINE:
        print("BETA_GOV_001 PASS: R18 baseline is active; future-unit manifest gate armed.")
        return

    manifest_rel = state.get("active_rebuild_manifest_path")
    if not manifest_rel:
        fail(
            "CURRENT_STATE advanced beyond R18 without active_rebuild_manifest_path"
        )

    manifest_path = ROOT / manifest_rel
    manifest = load_json(manifest_path)

    missing_keys = sorted(REQUIRED_MANIFEST_KEYS - set(manifest))
    if missing_keys:
        fail(f"rebuild manifest missing keys: {missing_keys}")

    if manifest.get("unit_id") != current_unit:
        fail(
            f"manifest unit_id {manifest.get('unit_id')!r} does not match "
            f"CURRENT_STATE last_verified_durable_unit {current_unit!r}"
        )

    if manifest.get("python_rebuild_ready") is not True:
        fail("python_rebuild_ready must be true before CURRENT_STATE advances")

    missing_artifacts = manifest.get("missing_required_artifacts")
    if missing_artifacts:
        fail(f"missing_required_artifacts is not empty: {missing_artifacts}")

    if not manifest.get("source_code"):
        fail("source_code must identify the authoritative producing code")

    if not manifest.get("outputs"):
        fail("outputs must identify the durable result artifacts")

    if not manifest.get("qa"):
        fail("qa must identify the verification evidence")

    if not manifest.get("github_commits"):
        fail("github_commits must record durable source/result revisions")

    reconstruction = manifest.get("reconstruction")
    if not isinstance(reconstruction, dict):
        fail("reconstruction must be an object")

    missing_recon = sorted(REQUIRED_RECONSTRUCTION_KEYS - set(reconstruction))
    if missing_recon:
        fail(f"reconstruction missing keys: {missing_recon}")

    if not reconstruction.get("entry_point"):
        fail("reconstruction.entry_point must be populated")
    if not reconstruction.get("timing_semantics"):
        fail("reconstruction.timing_semantics must be populated")

    verification = manifest.get("verification")
    if not isinstance(verification, dict):
        fail("verification must be an object")
    if verification.get("github_readback") is not True:
        fail("verification.github_readback must be true")
    if verification.get("hashes_verified") is not True:
        fail("verification.hashes_verified must be true")

    drive_artifacts = manifest.get("drive_artifacts") or []
    if drive_artifacts and verification.get("drive_readback") is not True:
        fail("Drive artifacts exist but verification.drive_readback is not true")

    print(
        "BETA_GOV_001 PASS: future scientific unit has a rebuild-ready durable manifest:",
        manifest_rel,
    )


if __name__ == "__main__":
    main()
