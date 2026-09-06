from __future__ import annotations

from market.constants import PROVIDER_CONFLICT
from market.models import MarketObservation


class DemoConflictProvider:
    name = PROVIDER_CONFLICT

    def get_current_observation(self, symbol: str, replay_state):
        return (
            MarketObservation.objects.filter(symbol=symbol, provider=self.name, as_of__lte=replay_state.current_as_of, received_at__lte=replay_state.current_as_of)
            .order_by("-as_of", "-received_at", "-id")
            .first()
        )
