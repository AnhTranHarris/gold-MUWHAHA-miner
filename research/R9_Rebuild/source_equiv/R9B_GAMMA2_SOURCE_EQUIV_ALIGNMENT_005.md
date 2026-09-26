# R9B_GAMMA2_SOURCE_EQUIV_ALIGNMENT_005
# January-only source-equivalence diagnostic.
# Exact executable source SHA-256:
# 5b71250376d7d6ae98ebcc1735e6c2c26585c005992f9e90c239bb7e912c236c
#
# Reused frozen causal cache:
# MM_C30_B1B_M01_CAUSAL_CACHE.npz
# SHA-256 71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5
#
# Tested authoritative modeled-bid R8 sweep semantics under the two count-bracketing
# CONT side-effect variants from SEMANTICS_004, but replaced reconstructed
# multiscale context with the exact frozen completed 1m/3m/5m/10m/20m
# align_long / align_short arrays and frozen completed-M5 ATR.
#
# Outcome: quota_only = 27,749 trades, cooldown_only = 34,164 trades.
# Both remain ~68.4% winners and negative, versus certified Gamma_2
# 30,943 trades / 81.983% winners / +$5,131.051 January net.
#
# Conclusion: completed multiscale alignment-cache arithmetic is not the source
# of the Gamma_2 reconstruction gap. The next source-equivalence hypothesis is
# full R8 position-occupancy ownership: CONT trades may suppress later sweep
# opportunities while a position is live and cooldown starts only after close.
