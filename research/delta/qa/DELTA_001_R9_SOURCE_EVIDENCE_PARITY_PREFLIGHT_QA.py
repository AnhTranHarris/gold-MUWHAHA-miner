from __future__ import annotations
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
r=json.loads((root/"research/delta/checkpoints/DELTA_001_RESULTS.json").read_text())
assert r["pass"] is True
assert all(r["checks"].values())
print("DELTA_001_QA PASS")
