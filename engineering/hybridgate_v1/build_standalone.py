"""Build the full source-exact HybridGate standalone EX5 candidate.

The 88 selected packed trees are compile-time resources, not runtime files.
No network, fitting, historical-data reads, DLL or terminal modification.
Native compilation and execution certification remain separate gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from prepare_install import ROOT, HERE, stage, sha_file, require

PARENT = "699da4f68239b8029a9e61e272e650f90c365de5"
BASE = Path("MQL5/Experts/HybridGateV1/GoldMuwahahaMiner_HybridGateV1.mq5")
EA = Path("MQL5/Experts/HybridGateStandalone/GoldMuwahahaMiner_HybridGateStandalone.mq5")
HEADER = EA.with_name("HG7EmbeddedModels.mqh")
MODEL_MANIFEST = Path("MQL5/Scripts/HybridGateQC/HG5QCManifest.mqh")
RESOURCE_DIR = Path("MQL5/Files/HG7EM")
MODEL_DIR = Path("MQL5/Files/HG5QC")
MODEL_COUNT = 88
MAX_MODEL_BYTES = 67108864


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def replace_once(text: str, before: str, after: str) -> str:
    require(text.count(before) == 1, "unexpected frozen EA anchor: " + before)
    return text.replace(before, after, 1)


def expected_ea(source: str) -> str:
    # Allowed packaging-only transformations; reject any other difference.
    source = replace_once(
        source,
        "// SECTION 00 — exact tester asset declarations; native transfer still requires QC.",
        "// SECTION 00 — all 88 frozen model assets embedded at compile time; native QC pending.",
    )
    source, n = re.subn(r"^#property tester_file .*\n", "", source, flags=re.M)
    require(n == MODEL_COUNT, "unexpected tester_file count")
    for old, new in (
        ('#property version   "2.06"', '#property version   "2.07"'),
        ('#property description "Human Approved HybridGate V1 — tester-only integration candidate; demo/live execution locked"',
         '#property description "HybridGate V1 standalone embedded model candidate; demo/live execution locked"'),
        ('#include <HybridGateV1/HG5FileAdapter.mqh>', '#include "HG7EmbeddedModels.mqh"'),
        ('g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST":"_OBS");',
         'g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST_EMBED":"_OBS_EMBED");'),
        (r'HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",HG_MODEL_SHA[i],67108864,bytes)',
         'HG7ReadEmbedded(i,HG_MODEL_SHA[i],bytes)'),
    ):
        source = replace_once(source, old, new)
    require(len(re.findall(r"\bHG6_BUILD_ID\b", source)) == 2, "build identity anchors")
    return re.sub(r"\bHG6_BUILD_ID\b", "HG7_BUILD_ID", source)


def array_field(source: str, field: str) -> list[str]:
    m = re.search(r"string " + re.escape(field) + r"\[\]=\{([^}]+)\};", source)
    require(m is not None, "missing manifest field " + field)
    return json.loads("[" + m.group(1) + "]")


def expected_header(ids: list[str]) -> str:
    prefix = """#ifndef HG7_EMBEDDED_MODELS_MQH
#define HG7_EMBEDDED_MODELS_MQH
// Exact frozen HG5 model order; build_standalone.py verifies aliases and bytes.
// Resource variables are read-only; only the current model is copied to the
// existing parser, then released. The SHA-256 check precedes every Load().
#define HG7_BUILD_ID "HG7-embedded-699da4f68239b8029a9e61e272e650f90c365de5-v1"
"""
    resources = "\n".join(
        rf'#resource "\\Files\\HG7EM\\{i:03d}.bin" as uchar HG7M{i:03d}[] // {name}'
        for i, name in enumerate(ids)
    )
    body = """
bool HG7CopyVerified(const uchar &source[],const string expected,uchar &data[]){
 ArrayFree(data);
 int n=ArraySize(source);
 if(n<=0||n>67108864||ArrayResize(data,n)!=n)return false;
 if(ArrayCopy(data,source,0,0,n)!=n){ArrayFree(data);return false;}
 uchar key[],digest[];
 if(CryptEncode(CRYPT_HASH_SHA256,data,key,digest)!=32){ArrayFree(data);return false;}
 string hex="";for(int i=0;i<32;i++)hex+=StringFormat("%02x",(uint)digest[i]);
 if(hex!=expected){ArrayFree(data);return false;}
 return true;
}
bool HG7ReadEmbedded(const int index,const string expected,uchar &data[]){
 switch(index){
"""
    cases = "\n".join(
        f"  case {i}: return HG7CopyVerified(HG7M{i:03d},expected,data);"
        for i in range(len(ids))
    )
    return prefix + resources + body + cases + """
  default: ArrayFree(data);return false;
 }
}
#endif
"""


def verify_source(root: Path) -> list[tuple[str, str]]:
    qc = json.loads(read_text(root / "engineering/hybridgate_v1/QC_INSTALL_MANIFEST.json"))
    native = json.loads(read_text(root / "engineering/hybridgate_v1/NATIVE_SOURCE_MANIFEST.json"))
    source_pins = {
        **{k: v for k, v in qc.items() if k.startswith("MQL5/Scripts/")},
        **native,
    }
    require(len(source_pins) == 39, "unexpected frozen source count")
    for rel, digest in source_pins.items():
        require((root / rel).is_file() and sha_file(root / rel) == digest,
                "frozen source integrity failure: " + rel)
    m = read_text(root / MODEL_MANIFEST)
    ids, hashes = array_field(m, "HG_ID"), array_field(m, "HG_MODEL_SHA")
    require(len(ids) == len(hashes) == len(set(ids)) == MODEL_COUNT, "model count/order")
    require(sum(k.endswith(".hg5p") for k in qc) == MODEL_COUNT, "packed model count")
    for name, digest in zip(ids, hashes):
        require(re.fullmatch(r"[A-Za-z0-9_]+", name) is not None, "unsafe model identifier")
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "invalid digest")
        require(qc.get((MODEL_DIR / (name + ".hg5p")).as_posix()) == digest,
                "model hash mismatch: " + name)
    source = read_text(root / BASE)
    declarations = re.findall(r'^#property tester_file "HG5QC\\\\([^"]+)\.hg5p"$',
                              source, flags=re.M)
    require(declarations == ids, "frozen tester declaration order mismatch")
    require(read_text(root / EA) == expected_ea(source), "standalone EA differs beyond approved packaging changes")
    require(read_text(root / HEADER) == expected_header(ids), "embedded adapter differs from exact generator")
    return list(zip(ids, hashes))


def build(root: Path, assets: Path, dest: Path) -> dict:
    require(not dest.exists() and not dest.is_symlink(), "destination already exists; never overwrite")
    models = verify_source(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".hg7-build-", dir=dest.parent) as tmp:
        work = Path(tmp) / "staged"
        stage(root, assets, work, runtime_only=True)
        manifest_path = work / "INSTALL_MANIFEST.json"
        manifest = json.loads(read_text(manifest_path))
        mapping = []
        for i, (name, digest) in enumerate(models):
            old = (MODEL_DIR / (name + ".hg5p")).as_posix()
            new = (RESOURCE_DIR / f"{i:03d}.bin").as_posix()
            require(manifest.get(old) == digest, "missing staged model " + name)
            p, q = work / old, work / new
            require(0 < p.stat().st_size <= MAX_MODEL_BYTES, "resource size out of bounds: " + name)
            require(sha_file(p) == digest, "resource bytes mismatch: " + name)
            q.parent.mkdir(parents=True, exist_ok=True)
            p.rename(q)
            del manifest[old]
            manifest[new] = digest
            mapping.append({"index": i, "model": name, "resource": new,
                            "sha256": digest, "bytes": q.stat().st_size})
        (work / MODEL_DIR).rmdir()
        (work / BASE).unlink()
        del manifest[BASE.as_posix()]
        for rel in (EA, HEADER):
            target = work / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, target)
            manifest[rel.as_posix()] = sha_file(root / rel)
        require(all(sha_file(work / k) == v for k, v in manifest.items()),
                "final staged file hash mismatch")
        actual = {p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file()}
        require(actual == set(manifest) | {"INSTALL_MANIFEST.json"}, "unregistered staged file")
        require(not any(p.endswith((".hg5p", ".hg5f", ".npz", ".csv", ".gz", ".dll", ".exe"))
                        for p in manifest), "unexpected external runtime or research asset")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt = {
            "status": "STAGED_SOURCE_ONLY_NATIVE_COMPILE_NOT_RUN",
            "parent": PARENT,
            "entry_point": EA.as_posix(),
            "model_count": MODEL_COUNT,
            "resource_bytes": sum(x["bytes"] for x in mapping),
            "resources": mapping,
            "manifest_sha256": sha_file(manifest_path),
            "native_acceptance": "0/33; resource-specific native QC also pending",
            "execution_authorization": "none",
        }
        (work / "STANDALONE_BUILD_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        require(not dest.exists() and not dest.is_symlink(), "destination appeared during build")
        os.rename(work, dest)
    return receipt


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--assets", type=Path)
    p.add_argument("--dest", type=Path)
    p.add_argument("--verify-source", action="store_true")
    a = p.parse_args()
    if a.verify_source:
        require(a.assets is None and a.dest is None, "--verify-source is standalone")
        models = verify_source(a.root.resolve())
        print(json.dumps({"status": "SOURCE_PACKAGING_CONTRACT_PASS", "models": len(models),
                          "parent": PARENT, "native_compile": "NOT_RUN"}, indent=2))
        return
    if a.assets is None or a.dest is None:
        p.error("--assets and --dest are required")
    print(json.dumps(build(a.root.resolve(), a.assets.resolve(), a.dest.absolute()), indent=2))


if __name__ == "__main__":
    main()
