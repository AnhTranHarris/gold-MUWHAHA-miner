"""Restore the immutable R00-053A/B/C evidence ZIP from its nine Drive chunks.

Place the nine .chunkNN_of_09 files and JSON manifest in one directory, then
run this script from that directory. No market-source files are changed.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import json

manifest = json.loads(Path("R00_053_RESEARCH_FULL_RECOVERY_CHUNKS_MANIFEST.json").read_text())
output = Path(manifest["full_archive"])
with output.open("wb") as target:
    for part in manifest["parts"]:
        raw = Path(part["name"]).read_bytes()
        assert len(raw) == part["bytes"]
        assert sha256(raw).hexdigest() == part["sha256"]
        target.write(raw)
assert output.stat().st_size == manifest["full_bytes"]
assert sha256(output.read_bytes()).hexdigest() == manifest["full_sha256"]
with ZipFile(output) as archive:
    assert archive.testzip() is None
print("Verified:", output, manifest["full_sha256"])
