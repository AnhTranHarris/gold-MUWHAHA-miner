# F401 Stage0 original GitHub source: fresh member-manifest SHA-256 verification — 2026-10-26
Scope: exact content returned by authenticated GitHub fetch_file from branch `carson/htf-f401-emergency-preservation-20261026`. Four original source/JSON bytes verified against repository `F401_MEMBER_MANIFEST.json`. Not raw recovery ZIP validation, not new tests against market data, not owner approval.

SHA-256 digest code was self-tested against ASCII "abc" => `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` (PASS), then applied to UTF-8 bytes of fetched complete file content:

| Original GitHub source member | Bytes | Fresh SHA-256 | Manifest match | Git blob SHA |
|---|---:|---|---|---|
| f401_preorder_marked_information.py | 14,210 | `85340d0649838fd7fd31de033628ebf0169e8233ef0818f254f45569e6b2ebee` | PASS | `c2274dd03b1537d18fed299838f634cd338b696c` |
| f401_incremental_information_screen.py | 8,096 | `687e1365f6a1240f97a23f3c07dc816f27f2ed73097b1534b85b7c67c6d5c80d` | PASS | `09352ecc8171f8819e2694f251c4d0e61330c628` |
| test_f401_preorder_causality.py | 1,861 | `cfe8b11be7583fdc6665cf0743d290a570e6edb32d5618a5f5a5b5b77a097491` | PASS | `394be8656d9d115b5b07ebbd69e66b608136561f` |
| F401_RECOVERY_RECEIPT.json | 2,380 | `9302c4744ced8b21c97fd6b3deaf9012076818fb6fe8bd3f4313156bc5c8f640` | PASS | `b5c7defd5be43af1f201d2353c6cd407e3e6c7ed` |

This audit verifies source text *on the existing GitHub preservation branch*, without modifying it. These four digest checks do **not** establish SHA/CRC of the absent 59,985B conversation recovery kit or 112,434,148B original R17 source/weights ZIP. Existing 4/4 Stage0 fixture PASS is a historical receipt, not a newly executed test. Original F395/F398 cloud binary SHA values remain historical; only authenticated Drive metadata/folder ownership was freshly inspected. No original market tapes scored in this session. The current source-exact research cursor is M-DK-01 after signed R10 owner exception, 21/39 accepted historical objectives, all G gates open. Refer to sibling `F401_R17_NEW_CHAT_RECOVERY_AUDIT_MDK01_CURSOR_20261026.md` for complete missing-binary details and next action.
