# F401-R110-DIST: preserved conditional-distribution experiment

UNAPPROVED research. This is a sibling experiment scientifically based on R109,
not the action-space R110/R111 report already committed separately. The shared
continuation remains **R112**. See `SCIENTIFIC_REPORT.md` for measured results,
exposure, limits and the parked configuration. `PLAN.md` is the unchanged plan
written before fitting; its historical R110 name is retained for hash integrity.

The archive includes original tested source, 36 fitted models, four complete
monthly score files, all frozen masks, independent recount, logs, dependency
versions, source hashes and exact reused engine modules. The large feature cache
is reproducible and omitted. Original market tapes and FILTER08 remain in their
authorized existing source locations; they are not duplicated into this archive.

## Reproduce the archived run

Use Python 3.12 and `research_r110/requirements.txt`. Extract the archive into a
new directory and keep its directory layout. Place these already-authorized,
hash-verified originals in its `sources/` directory:

* `filter08_recovered.zip` (the original full FILTER08 archive; name is local only).
* `XAUUSD_DUKAS_2026_01_ticks.csv.gz`
* `XAUUSD_DUKAS_2026_02_ticks.csv.gz`
* `XAUUSD_DUKAS_2026_06_ticks.csv.gz`
* `XAUUSD_DUKAS_2026_07_ticks.csv.gz`

Verify the SHA256 values in `SOURCE_CONTRACT.json` before use. Do not substitute
other downloads, derived bars, brokers, labels or different month revisions.
Run from the extracted root:

```bash
python -m unittest discover -s research_r110 -p test_causality.py -v
python research_r110/run.py prepare --month 01
python research_r110/run.py prepare --month 02
python research_r110/run.py prepare --month 06
python research_r110/run.py prepare --month 07
python research_r110/run.py score --month 01
python research_r110/run.py score --month 02
python research_r110/run.py score --month 06
python research_r110/run.py score --month 07
python research_r110/run.py evaluate
python research_r110/verify_saved.py
```

These commands rescore the supplied frozen models. For a fit reproduction, use a
fresh extraction with an empty `research_r110/models/` directory, run January
preparation, then `python research_r110/run.py fit` before scoring. Never mix
models from different experiments: the original fit implementation resumes any
existing named checkpoints and does not authenticate their training contract.
`verify_saved.py` authenticates this archive's frozen models against its manifest.

The repository copy preserves the same tested `run.py`; it expects the archive
layout above. It is not a drop-in installation into the live EA. No order API is
called. Do not load joblib files from an unverified source.

## Continuity before another experiment

Refresh the original governor v1.4+A1/A2/A3 and dated owner directives, whole-EA
charter, source authorization, original FILTER08 forensic audit, 39-objective
checklist and latest live ledger. The ledger is:
https://docs.google.com/document/d/1SOiAbTGROPPgSlj_bQfZMTKg-2DQ22PQqmP03fRS0GE/edit

Resolve the newest Git branch/commit as well; at this publication check the
R110/R111 action report was newer than the ledger's R109 ending. Its commit was
`ad4b551d224233d889c4c897e57d23bf027b587a`, a direct child of R109. This archive
does not reset that cursor. Do not infer a complete bootstrap from file retrieval
alone: original appendices need to be reviewed for the intended new experiment.
This receipt is not an automatic future-chat enforcement mechanism.

Keep PRIMARY read-only, put unapproved research in MT5_EXPAND /01, and reserve /02
for explicit owner-approved artifacts. Current verified acceptance remains
21/39 historical research-only; M-DK-01, four DK monthly objectives, S01–S05 and
G01–G09 remain open. Do not repeat this density configuration or its calibration
grid. The action-specific R112 continuation is a different unexecuted lead here.
