from __future__ import annotations

from market.constants import PROVIDER_REPLAY, SYMBOL_BENCHMARKS
from market.models import MarketBar, MarketObservation
from .base import MarketProvider


class DemoReplayProvider(MarketProvider):
    name = PROVIDER_REPLAY

    def get_current_observation(self, symbol: str, replay_state):
        return (
            MarketObservation.objects.filter(symbol=symbol, provider=self.name, as_of__lte=replay_state.current_as_of, received_at__lte=replay_state.current_as_of)
            .order_by("-as_of", "-received_at", "-id")
            .first()
        )

    def get_historical_bars(self, symbol: str, before_as_of, limit: int):
        return list(
            MarketBar.objects.filter(symbol=symbol, provider=self.name, as_of__lt=before_as_of)
            .order_by("-as_of")[:limit]
        )[::-1]

    def get_observations_between(self, symbol: str, start, end):
        return MarketObservation.objects.filter(symbol=symbol, provider=self.name, as_of__gt=start, as_of__lte=end, received_at__lte=end).order_by("as_of")

    def get_benchmark_symbol(self, symbol: str) -> str:
        return SYMBOL_BENCHMARKS[symbol]
