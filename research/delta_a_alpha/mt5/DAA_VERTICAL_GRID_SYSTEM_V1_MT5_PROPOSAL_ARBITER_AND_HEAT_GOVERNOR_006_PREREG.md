# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 006
## Proposal Arbiter and Heat Governor

**Status:** IMPLEMENTATION CONTRACT  
**Parent:** unit 005 native routing + recovery  
**Execution:** no order-send path

## Objective

Unify all V1 decision layers into one account-level physical-risk decision.

Candidate owners:
- SESSION
- WATCHDOG
- NATIVE
- RECOVERY

## Arbitration

- inactive/zero-direction candidates are ignored;
- same-direction candidates merge into one consensus proposal;
- opposite-direction candidates create a hard conflict and fail closed;
- attribution priority for aligned proposals is RECOVERY > WATCHDOG > NATIVE > SESSION;
- attribution priority never changes direction.

## Capacity

The governor enforces:
- global cap;
- session cap;
- source/layer cap.

All V1 caps default to 620 in this engineering skeleton so the interfaces exist without silently importing a month-specific capacity choice. V2+ tuning may change them.

London-open and rollover remain observe-only.

## Position tag contract

Future physical orders use comments shaped as:

`DAA_V1|SOURCE|SESSION|EVENT`

This lets the governor count global, source and session ownership independently.

## Acceptance

- conflict fails closed;
- aligned proposals merge;
- execution-disabled state is observe-only;
- global/session/layer caps can each block new risk;
- no order-send path exists;
- deterministic CI QA passes.

## Next certification step

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_SKELETON_CERTIFICATION_007`

Unit 007 is a skeleton-wide static/parity certification package. It does not add strategy alpha.
