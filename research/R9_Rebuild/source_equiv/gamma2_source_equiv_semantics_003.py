# R9B_GAMMA2_SOURCE_EQUIV_SEMANTICS_003
# Durable source SHA-256: c5b0703134888549c41f633ae2ab7b32d2f5f829d415aefc3f8b0e9d60a9ca4b
# The exact executable source is preserved in the research runtime; this durable mirror records the tested semantics contract.
SEMANTICS = {
  "scope": "January 2026 Dukascopy exact ordered ticks",
  "price_bases_tested": ["modeled_bid_completed_seconds", "modeled_mid_completed_seconds"],
  "cont_transition": "valid CONT resets/invalidate active sweep setup",
  "cont_consumes_sweep_quota": False,
  "cont_sets_sweep_cooldown": False,
  "sweep_quota_per_minute": 5,
  "sweep_cooldown_seconds": 1,
  "gamma2_target_trades": 30943,
  "gamma2_target_winners": 25368,
  "gamma2_target_win_rate": 0.8198300100184209
}
