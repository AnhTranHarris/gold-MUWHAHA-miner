# Artifacts

This directory stores compact checkpoint manifests, schemas, hashes, and reproducibility metadata.

Large raw or derived datasets stay in their registered external durable store. Never commit large tick corpora to GitHub.

A checkpoint manifest must make it possible for a future session to answer:
- exactly what ran;
- against which data;
- with which code/config bytes;
- what it produced;
- whether it passed;
- what unit comes next.
