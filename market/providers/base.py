from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class MarketProvider(ABC):
    name: str

    @abstractmethod
    def get_current_observation(self, symbol: str, replay_state):
        raise NotImplementedError

    @abstractmethod
    def get_historical_bars(self, symbol: str, before_as_of, limit: int) -> Iterable:
        raise NotImplementedError

    @abstractmethod
    def get_observations_between(self, symbol: str, start, end) -> Iterable:
        raise NotImplementedError

    @abstractmethod
    def get_benchmark_symbol(self, symbol: str) -> str:
        raise NotImplementedError
