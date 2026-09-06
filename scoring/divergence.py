from __future__ import annotations

from .constants import BENCHMARK_WEIGHT, NORMALIZATION_CAP
from .volatility import component_points


def calculate_residual_return(stock_return: float, benchmark_return: float) -> float:
    return stock_return - benchmark_return


def benchmark_divergence_ratio(residual_return: float, expected_residual_gap_volatility: float) -> float:
    if expected_residual_gap_volatility <= 0:
        return 0.0
    return residual_return / expected_residual_gap_volatility


def benchmark_component_points(ratio: float) -> float:
    return component_points(ratio, BENCHMARK_WEIGHT, NORMALIZATION_CAP)
