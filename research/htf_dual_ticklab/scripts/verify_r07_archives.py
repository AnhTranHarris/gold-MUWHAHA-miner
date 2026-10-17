"""Verify R07 raw broker-derived study bundles by exact committed SHA-256.

Usage: python verify_r07_archives.py <research.zip> <quote_features.zip>
This reads local downloaded copies. Never fetches external quotes or silently
accepts unregistered source files.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import json, sys

EXPECTED={
    "XAUUSD_HTF_R07_Complete_Research_and_Trade_Ledgers.zip":
        "aec1b65eb361eee76132c72954ec969be1759d6da2d67cdbb0fc01ef39ee6dd8",
    "XAUUSD_HTF_R07_Quote_Asymmetry_Features.zip":
        "8d48e122d2915784d59d4943fa97be265a650967815dbb85047ac82efec403ab",
}

def verify(path: Path)->dict:
    path=Path(path)
    if path.name not in EXPECTED:
        raise ValueError("not an R07 exact-name authorized bundle")
    if sha256(path.read_bytes()).hexdigest()!=EXPECTED[path.name]:
        raise ValueError("R07 archive SHA-256 mismatch")
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
        manifest=json.loads(archive.read("SHA256_CONTENT_MANIFEST.json"))
        if manifest["study"]!="XAU-HTF-20261016-R07-QUOTE-FLOW-PATH-AUCTION":
            raise ValueError("wrong frozen experiment")
        expected_members={x["path"]:x for x in manifest["members"]}
        actual=set(archive.namelist())-{"SHA256_CONTENT_MANIFEST.json"}
        if actual!=set(expected_members):
            raise ValueError("missing, duplicate or extra data members")
        for name, item in expected_members.items():
            data=archive.read(name)
            if len(data)!=item["bytes"] or sha256(data).hexdigest()!=item["sha256"]:
                raise ValueError("member integrity mismatch: "+name)
    return {"name":path.name,"members":len(expected_members),"valid":True}

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("provide exactly both locally downloaded authorized R07 ZIP files")
    results=[verify(Path(arg)) for arg in sys.argv[1:]]
    if {a["name"] for a in results}!=set(EXPECTED):
        raise SystemExit("both different canonical archives are required")
    print(json.dumps(results,indent=2))
