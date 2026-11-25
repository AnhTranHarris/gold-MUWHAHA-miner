"""Position sizing from realized USD balance, expressed as integer cents."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from numba import njit
STEP_CENTS=500_000
@njit(cache=True)
def lot_units(balance_cents, enabled, max_units):
    if balance_cents<=0: return 0
    if not enabled: return 1
    return min(max_units,1+balance_cents//STEP_CENTS)
@dataclass(frozen=True)
class LadderConfig:
    enabled: bool=False
    max_lot: str='0.10'
    def __post_init__(self):
        if type(self.enabled) is not bool: raise ValueError('enabled must be boolean')
        try: n=Decimal(str(self.max_lot))*100
        except InvalidOperation as e: raise ValueError('Invalid lot cap') from e
        if not n.is_finite() or n<1 or n>100 or n!=n.to_integral_value():
            raise ValueError('max_lot must be 0.01 through 1.00 in 0.01 increments')
    @property
    def max_units(self): return int(Decimal(str(self.max_lot))*100)
    def units(self, realized_balance_cents):
        if type(realized_balance_cents) is not int: raise TypeError('Use integer USD cents')
        return int(lot_units(realized_balance_cents,self.enabled,self.max_units))
