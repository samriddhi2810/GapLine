from __future__ import annotations

import math
from decimal import Decimal
from typing import Iterable

from .constants import MIN_VOLATILITY_EPSILON


def as_float(value: Decimal | float | int) -> float:
    return float(value)


def calculate_returns(prices: Iterable[Decimal | float | int]) -> list[float]:
    values = [as_float(price) for price in prices]
    returns: list[float] = []
    for previous, current in zip(values, values[1:]):
        if previous <= 0:
            continue
        returns.append(current / previous - 1)
    return returns


def sample_standard_deviation(values: Iterable[float]) -> float:
    data = list(values)
    if len(data) < 2:
        return 0.0
    mean = sum(data) / len(data)
    variance = sum((value - mean) ** 2 for value in data) / (len(data) - 1)
    return math.sqrt(variance)


def expected_gap_volatility(daily_volatility: float, trading_days: int) -> float:
    return max(daily_volatility, MIN_VOLATILITY_EPSILON) * math.sqrt(max(trading_days, 1))


def component_points(ratio: float, weight: int, cap: float) -> float:
    return min(abs(ratio), cap) / cap * weight
