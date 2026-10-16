"""Read-only verification of approved HTF R02 experimental source archive.

Usage: python verify_r02_archive.py downloaded_R02.zip

This script does NOT execute research strategies or extract files.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

EXPECTED_SHA256 = "05ac4819e993c1ea07a11faf94af8848459706c9e0baefbc9f9bf6cdd0e386ba"

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python verify_r02_archive.py R02.zip")
    path = Path(sys.argv[1])
    sha = hashlib.sha256()
    with path.open("rb") as src:
        for part in iter(lambda: src.read(1048576), b""):
            sha.update(part)
    if sha.hexdigest() != EXPECTED_SHA256:
        raise SystemExit("INVALID R02 ARCHIVE SHA256")
    with ZipFile(path) as z:
        if z.testzip() is not None:
            raise SystemExit("INVALID R02 ARCHIVE CRC")
        members = json.loads(z.read("SHA256_MEMBER_MANIFEST.json"))
        for item in members["archive_members"]:
            data = z.read(item["path"])
            if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise SystemExit("INVALID R02 SOURCE MEMBER: " + item["path"])
        if len(z.namelist()) != len(members["archive_members"]) + 1:
            raise SystemExit("INVALID R02 ARCHIVE MEMBER COUNT")
    print("R02_ORIGINAL_RESEARCH_SOURCE_VERIFIED", EXPECTED_SHA256)

if __name__ == "__main__":
    main()
