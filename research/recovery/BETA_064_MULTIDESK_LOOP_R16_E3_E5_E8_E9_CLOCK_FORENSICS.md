# BETA064 missing multidesk helper recovery — R16 E3/E5/E8/E9 clock forensics

**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA only; no Alpha/Gamma inspected  
**August:** SEALED  
**MQL5:** prohibited during helper recovery

## Bounded question

Continue R15 selected-timestamp clock reconstruction for E3, E5, E8 and E9. Historical LEFT-edge five-second state is used only to test whether the current broad mechanism masks could have been emitted solely on FALSE→TRUE transitions.

## Jan–Mar evidence

### E5 — edge behavior strongly supported

- Selected E5 rows: 183.
- Recovered broad-mask active at 176 / 183 = **96.1749%**.
- Among all 176 active matches, run age 0 = **100%**.
- No matching selected E5 row occurs at age >0.
- 176 active matches occupy 176 distinct broad runs; no repeated selected ownership inside one run.

**R16 disposition:** retain the scaffold's edge-only E5 emission. This is strong behavioral support, not line-for-line source proof.

### E9 — edge-only rejected

- Selected E9 rows: 508.
- Recovered broad-mask active at 488 / 508 = **96.0630%**.
- Age 0: 389 / 488 = **79.7131%**.
- Age >0: 99 / 488 = **20.2869%**.
- Active selected run ages observed: 0, 1, 2, 3 and 6 five-second bars.
- Each selected E9 row falls in a distinct broad run in the final selected ledger; horizon/one-position ownership can censor additional candidates.

**R16 conclusion:** the supported broad E9 mechanism cannot be emitted only on its FALSE→TRUE transition. Persistent in-state eligibility or a secondary within-state trigger is required.

**Safe forensic scaffold change:** E9 uses `edge_only=False` in the RECOVERY_UNCERTIFIED scaffold. This is not a claim that every active broad-mask row was an original candidate; exact hidden sub-gates and raw_score remain unknown.

### E8 — sparse and boundary-unresolved; no code change

- Selected E8 rows: 5.
- Broad-mask recall: 5 / 5.
- Run-age distribution: age0 = 3, age1 = 2.
- The existing scaffold explicitly marks the exact E8 prior-15m boundary as unresolved.

The five-row sample is sufficient to warn that the current broad-mask edge transform is not proven, but too sparse to promote direct persistent emission as the recovered rule. E8 remains unresolved.

### E3 — insufficient evidence; no code change

- Selected E3 rows: 2 across Jan–Mar.
- One matches the recovered broad mask at age0.
- One does not match the scaffold broad mask.
- The scaffold already marks the exact legacy ORB gate as unresolved.

E3 remains unresolved.

## R16 recovery matrix

| Desk | Broad-mask support | Edge-only status | Scaffold action |
|---|---|---|---|
| E3 | sparse / one mismatch | UNKNOWN | unchanged |
| E5 | 176/183 active; 176/176 at age0 | SUPPORTED | keep edge-only |
| E8 | 5/5 active; 2/5 at age1 | NOT PROVEN / sparse | unchanged |
| E9 | 488/508 active; 99 active selections after age0 | REJECTED | persistent forensic emission |

## Important limitations

- Final selected trades are ownership- and horizon-censored; selected timestamps cannot uniquely identify candidate debounce.
- Historical LEFT-edge state is not production semantics.
- Exact candidate `raw_score` remains unrecovered.
- Exact pre-ownership candidate surface remains unrecovered.
- One-second `qv_imb` remains UNKNOWN and one-second BETA064 `quote_pressure` equality remains unproven.
- No Checkpoint-03 parity claim is restored.

## Exact next action

1. Search remaining BETA-only archives/revisions for pre-ownership candidate or `raw_score` artifacts.
2. Reconcile E7/E10/E12 emission status only if needed to close candidate identity; do not broaden scope without evidence.
3. Build a complete historical LEFT-edge forensic parent candidate stream only after every desk is classified EXACT / BEHAVIORALLY_CONSTRAINED / UNKNOWN.
4. Compare FIT candidate count and identities against the frozen 30,579-row reference to localize the remaining 34-row mismatch.
5. Historical reproduction remains forensic-only; corrected RIGHT-edge replacement requires new training, validation and checkpoint naming before MT5.
