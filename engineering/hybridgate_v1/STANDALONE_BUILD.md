# HybridGate v2.07 — standalone native build candidate (Stage 7A)

**Status: source and packaging candidate; native compilation NOT RUN; execution certification NOT RUN.** Parent: `699da4f68239b8029a9e61e272e650f90c365de5` (v2.06). This branch adds a separate EA; no original strategy, fitted model, data, or release gate is modified.

## Build the isolated source tree

Requires Python 3.11+ (standard library only) and the two existing, exact dependency archives identified in `DEPENDENCY_PINS.json`. Download the archives from their existing Drive records into one local folder, keeping their original filenames:

- [Stage5_base](https://drive.google.com/file/d/1_7NlBjXJhaMinQ8KgBk9Egf95avIeqW1/view): R9_HYBRIDGATE_V1_STAGE5_PORTABLE_ENGINEERING_20261125.zip
- [Stage5_D_I](https://drive.google.com/file/d/1s_FJev13ZBiBiTDVVhb77VMFZqy0HMS2/view): R9_HYBRIDGATE_V1_STAGE5_D_I_ENGINEERING_QC_20261125.zip

Run from this branch's checkout:

```powershell
py -3 engineering/hybridgate_v1/build_standalone.py --verify-source
py -3 engineering/hybridgate_v1/build_standalone.py --assets "C:\HGAssets" --dest "C:\HG7Build"
py -3 engineering/hybridgate_v1/build_standalone.py --assets "C:\HGAssets" --dest "C:\HG7QC" --with-inference-qc
```

Destination directories must not exist. The builder checks all frozen source hashes and the exact 88 model IDs, order, bytes, and resource aliases. It renames the packed models to compile-time resource files without altering their bytes. The runtime-only staging tree contains no inference witnesses, raw tick history, training code, or file-backed model bank. The separate QC tree contains 88 inference witnesses for offline parity only. Preserve the generated INSTALL_MANIFEST.json, STANDALONE_BUILD_RECEIPT.json and NUMPY_LICENSE.txt.

Use a dedicated isolated MetaTrader 5 data directory for compilation. Place the staged MQL5 tree under that directory, with paths preserved (do not overwrite an existing working installation). Open MQL5/Experts/HybridGateStandalone/GoldMuwahahaMiner_HybridGateStandalone.mq5 in the corresponding MetaEditor and compile. The #resource paths resolve relative to the terminal's MQL5 directory. All 88 resources must exist at compile time. Preserve the full compile log and EX5 hash. Do not treat a staged source receipt as a successful compile.

## Native gates (not yet executed)

1. Compile the complete EA and separately compile MQL5/Scripts/HybridGateStandalone/HG7EmbeddedQC.mq5 from the QC tree. Require no compiler errors; investigate warnings. Record compiler and terminal builds.
2. Run HG7EmbeddedQC in the isolated terminal. Require all 88 heads, the original expected witness row total, zero raw differences, zero float32 differences, and max absolute score error <= 1e-14. Preserve per-head output and summary. No trading calls in this script.
3. Copy only the compiled EA EX5 into another clean observation/tester environment. Leave HG7EM and the HG5QC model bank absent there. Verify all 88 embedded models initialize successfully and the loader does not request external model files. Local MT5 history, account/symbol properties, generated state/journal files and the frozen runtime contract remain required; standalone refers to packaging of fitted models, not elimination of MT5 itself.
4. Execute the inherited native acceptance matrix and source-clock/history contract in the existing QC workflow. Compare the file-backed v2.06 and embedded v2.07 on the same frozen source history, including proposals, actual execution lifecycle, recovery, latency, and net results. Do not substitute another quote stream or loosen gates to obtain a pass. The separately scoped state files and build ID are intentional and are not interchangeable.
5. Keep the demo/live release lock unchanged. Tester execution is opt-in and conditional on the existing source, broker, and safety checks. A successful compile alone does not authorize any execution release.

References: [MQL5 resources](https://www.mql5.com/en/docs/runtime/resources), [MQL5 resource variables](https://www.mql5.com/en/book/advanced/resources/resources_variables), [existing native acceptance matrix](ACCEPTANCE_TESTS.csv), [native runtime contract](NATIVE_RUNTIME_CONTRACT.md).

Rollback: retain the untouched v2.06 branch and parent commit; do not copy v2.07 snapshots into the v2.06 namespace. Do not merge this candidate into the original R9 or release branch before native acceptance.
