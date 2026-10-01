# BETA064 missing multidesk helper recovery — R15 E6/E11 persistence and debounce forensics

**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA only; no Alpha/Gamma inspected  
**August:** SEALED  
**MQL5:** not authorized during helper recovery

## Bounded question

R13/R14 established that the universal FALSE→TRUE edge hypothesis is wrong. R15 tests the two highest-value missing clocks, E6 and E11, against the preserved C02C selected ledger and freshly reconstructed historical LEFT-edge five-second mechanism state from the original Jan–Mar Dukascopy ticks.

Historical LEFT-edge state is used **for forensics only**. No LEFT-edge runtime is being promoted.

## Data and reconstruction

- Preserved C02C selected ledger: 5,519 rows from the durable Checkpoint-02E reproducibility bundle.
- E6 Jan–Mar selected rows: 502.
- E11 Jan–Mar selected rows: 1,263.
- Raw market source: original Jan–Mar Dukascopy tick files.
- Five-second state reconstructed without qp/qv because the tested broad E6/E11 masks do not require those fields.
- Broad forensic masks are the R11/R13 supported masks:
  - E6 long: vwap_z <= -1.0 and eff300 <= 0.50.
  - E6 short: vwap_z >= +1.0 and eff300 <= 0.50.
  - E11 long: r15 > 0 and eff15 >= 0.55 and tick_z >= 0.50.
  - E11 short: r15 < 0 and eff15 >= 0.55 and tick_z >= 0.50.
- Run age 0 means the first five-second row where the broad mask becomes active; age 1 means the next active row, etc.

## E6 result — edge-only is decisively rejected

Across Jan–Mar:

- 499 / 502 selected E6 timestamps are inside the reconstructed broad E6 state: **99.4024% recall**.
- Of those 499 active matches, **0% occur at broad-mask run age 0**.
- **100% occur after the broad mask is already persistent.**
- Median run age is 717 five-second bars.
- Active selected ages range from 1 through 7,632 bars.
- 141 distinct broad E6 runs contain the 499 active selected rows.
- A single broad E6 run contains as many as **20 selected E6 positions**.
- Same-run selected gaps have a minimum of **180 seconds**, which equals the E6 specialist horizon. This is therefore censored by the one-position/horizon scheduler and must not be misread as the candidate-generator debounce.
- Selected run ages occupy all residue classes modulo 2, 3, 4, 5, 6, 9, 12, 18 and 36 bars. A fixed run-start periodic emitter is not supported.

**Conclusion:** E6 cannot be emitted only on FALSE→TRUE transition of the supported broad state. Persistent in-state candidate eligibility is required, though the exact hidden sub-gate/raw-score source remains unrecovered.

## E11 result — edge-only is decisively rejected

Across Jan–Mar:

- 1,263 / 1,263 selected E11 timestamps are inside the reconstructed broad E11 state: **100% recall**.
- Only **37.6880%** occur at broad-mask run age 0.
- **62.3120%** occur after the broad state is already active.
- Selected ages cover every integer from 0 through 9 bars, i.e. 0 through 45 seconds into the broad active run.
- 1,232 broad E11 runs contain the 1,263 selected rows.
- In the final selected one-position ledger there is at most one selected E11 per broad run; because E11 horizon is 45 seconds and these broad runs are short, final ownership strongly censors any underlying repeated candidate emission.

**Conclusion:** E11 cannot be a broad-mask edge-only clock. Persistent in-state eligibility or a secondary within-state trigger is required.

## Surviving source-style evidence

The authoritative corrected V2 source preserves exact E1/E2/E4 replacement emission. Its local `emit(mask,...)` iterates **every active mask index** using `np.flatnonzero(mask)`; there is no FALSE→TRUE edge transformation and no built-in debounce.

This does not prove the lost V1 helper used identical code for E6/E11, but it is independent BETA-only source-style evidence consistent with the selected-timestamp forensics.

## Safe scaffold repair

The uncertified recovery scaffold should stop forcing E6 and E11 through `edge(mask)`.

For those two desks only, forensic emission is changed to persistent mask-row emission (`edge_only=False`).

This is **not** a claim of exact recovered source. It only removes a mechanism that the preserved evidence disproves.

## What remains unknown

- Exact E6/E11 hidden sub-gates, if any.
- Exact E6/E11 raw_score arithmetic.
- Whether every active broad-mask row was a candidate or whether another condition created an in-state sub-clock.
- One-second quote_pressure and qv_imb source arithmetic from R14.
- Pre-ownership candidate/prediction surface and exact candidate parity.

## Next action

1. Use persistent E6/E11 forensic emission as the non-edge baseline.
2. Search for any source/fixture preserving raw_score or pre-ownership candidates.
3. Test E3/E8 and residual E5/E9 selected timestamps the same way: broad-state recall, run age, repeated same-run ownership, and whether edge-only is falsified.
4. Only after the desk clocks are constrained should historical LEFT-edge reproduction be attempted.
5. Any historical reproduction remains forensic-only; corrected RIGHT-edge retraining/revalidation is required for a new checkpoint.
