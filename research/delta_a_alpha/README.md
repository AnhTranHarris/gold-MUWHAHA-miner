# Delta-A-alpha

Delta-A-alpha is an isolated side-research lineage forked from the live `delta` head at `ac91fc43389a34f8ba380b58143f8e185589b106`.

## Isolation contract

- Main `delta` is read-only from this branch.
- Existing `delta-A*` branches are historical evidence only; they are not ancestors or promotion authorities.
- Nothing discovered here changes main DELTA unless the owner explicitly authorizes a later handoff.
- August remains sealed.
- MQL5 remains unauthorized until explicit owner approval.

## Research purpose

The side lineage exists to explore higher-throughput specialist ideas without slowing or contaminating the main DELTA integration work. The first family is `GRID-001`, a clean-room reconstruction of the supplied grid-trading tutorial.

## Documentation architecture

GitHub is the machine-reproducibility layer. Store code, helper modules, exact configs, manifests, hashes, schemas, compact result JSON, recovery pointers, and immutable checkpoint reports here.

Google Drive is the human-readable layer. Store the research index, white papers, checkpoint narratives, decisions, and handoffs there.

Do not put huge raw ticks in GitHub. Do commit their hashes, partitions, schemas, producer versions, and regeneration rules.

## Vertical-build rule

A useful helper is promoted immediately, not left trapped in chat. If logic is reused, non-trivial, required to reproduce a result, expensive to reconstruct, or scientifically useful even when a test fails, it becomes a durable artifact before the next dependent experiment.

Start every new session from `CURRENT_STATE.json`; do not reconstruct the project from conversation memory.


## Vertical Grid System V1 — permanent spine (owner-promoted 2026-10-08)

The owner has explicitly promoted the vertically integrated grid architecture into Delta-A-alpha as V1. This is a narrow owner-authorized exception to the earlier isolation rule; it imports the V1 architecture contract and supporting January/February evidence, not unrelated external lineage work.

Permanent order:

```text
ordered ticks
→ session-specific grid geometry
→ completed H4/H1/M15/M5 structure
→ London/overlap/NY hourly high-volume harvesting + separate Asia geometry
→ Watchdog/regime renewal
→ trend-within-trend native routing
→ wrong-direction recovery
→ portfolio heat/capital governor
```

Machine spec: `research/delta_a_alpha/architecture/DAA_VERTICAL_GRID_SYSTEM_V1_SPEC.md`  
Manifest: `research/delta_a_alpha/artifacts/DAA_VERTICAL_GRID_SYSTEM_V1_MANIFEST.json`  
GitHub whitepaper: `research/delta_a_alpha/whitepapers/DAA_VERTICAL_GRID_SYSTEM_V1_WHITEPAPER.md`  
Google whitepaper: https://docs.google.com/document/d/1-PiyhfhulLl1garjwtSYOysPGOgBTgV_apnQmCKoCTc/edit?usp=drivesdk

V2, V3 and later refine the V1 layers month-by-month and later add small-capital survivability. They do not silently replace the spine. The owner has authorized the next unit: a faithful MT5 V1 engineering port with layer-by-layer parity diagnostics.


## Mandatory owner governance — any-time startup and blind holdouts (2026-10-08)

**AUTHORITATIVE GOVERNING RULE:** [Anytime-start / five-minute order-readiness / Jan–Jul development / August–September sealed holdouts](governance/DAA_ANYTIME_START_FIVE_MINUTE_READINESS_AND_BLIND_HOLDOUT_RULE.md).

The complete L0–L8 trading EA must be trade-capable by **T0 + 300 seconds** at any valid active-market deployment with pre-T0 historical context; it may emit qualified opportunities on its first actionable live ticks. Rolling online learning can improve performance but cannot block initial trading. Never force a trade against risk controls or promise profitability within five minutes. January–July are design months, **August is sealed** and **September reserved as a second owner-released blind holdout**. Historical as-of tests cannot train on information after their simulated start. The strategy remains self-adjusting inside the permanent V1 spine; small-capital qualification tiers are $100,000, $1,000, $500, $300, $100.
