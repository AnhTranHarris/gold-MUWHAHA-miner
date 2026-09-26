# R9B Event-Time Accuracy Owner Candidate
# Research-only deterministic reconstruction.
# Derived from Jan-Mar activity-anchor trades; April calibration.
# Not formally Gamma-promoted because May-Jul family behavior had already been observed
# before this exact owner was durably frozen.

def keep_event_time_entry(
    s1_disp_al: float,
    signal_delay_s: float,
    range_atr: float,
) -> bool:
    """
    Accuracy-first owner reconstructed from the depth-4 / min-leaf-1000
    Jan-Mar continuation-quality tree at the robust 0.51-0.54 decision plateau.

    Inputs are causal at the activity-anchor trigger.
    Returns True to permit the activity-anchor trade, False to abstain.
    """
    if s1_disp_al <= 1.040500:
        return False
    if s1_disp_al <= 1.426750:
        return signal_delay_s > 4.374500
    if s1_disp_al <= 2.502500 and signal_delay_s <= 1.663500:
        return range_atr <= 0.194659
    return True
