# Experiments

Every experiment lives in a bounded unit with an immutable input config and a compact durable result.

Required naming:
`DAA_<FAMILY>_<NNN>_<short-name>`

Required output:
- config/spec;
- producer path + commit/blob;
- dataset partition + canonical source hash;
- result JSON;
- decision note;
- checkpoint manifest if the result changes the research queue.

Do not create anonymous `temp.py`, `final2.py`, `results_new.csv`, or chat-only helper logic that later experiments depend on.
