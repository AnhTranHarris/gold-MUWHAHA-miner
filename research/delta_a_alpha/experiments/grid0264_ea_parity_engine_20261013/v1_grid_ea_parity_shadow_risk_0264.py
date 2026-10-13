"""GRID0264 shadow marked-equity correction: reserve expected roundtrip fee.

Legacy GRID0259 research mark counted unrealized price PnL but omitted the
already economically committed modeled roundtrip fee on still-open trades,
which could overstate available risk capital during high-velocity operation.
No change to the settlement cash ledger or original accepted source.
"""
from __future__ import annotations
from v1_grid_observed_lifecycle_0262_hardened import HardenedObservedLifecycleFundingEngine

class CostReservedObservedFundingEngine0264(HardenedObservedLifecycleFundingEngine):
    def _mark(self,q):
        base=super()._mark(q)
        reserve=sum(self.spec.roundtrip_usd_per_lot*p.lot for p in self.open)
        return base-reserve
    def summary(self):
        result=super().summary()
        result['reserved_expected_exit_fees_for_open_usd']=sum(
            self.spec.roundtrip_usd_per_lot*p.lot for p in self.open)
        result['net_fee_aware_marked_equity']=self._mark(self.last_quote) if self.last_quote else self.cash
        result['execution']='HYPOTHETICAL_RESEARCH_ONLY_NO_MT5_CASH_CERTIFICATION'
        return result
