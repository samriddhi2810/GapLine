from __future__ import annotations

from dataclasses import dataclass

from .constants import ATTENTION_THRESHOLD, NORMALIZATION_CAP, OWN_WEIGHT
from .divergence import benchmark_component_points, benchmark_divergence_ratio, calculate_residual_return
from .reversal import detect_reversal
from .volatility import component_points, expected_gap_volatility


@dataclass(frozen=True)
class ScoreResult:
    stock_return: float
    benchmark_return: float
    residual_return: float
    expected_gap_volatility: float
    expected_residual_gap_volatility: float
    own_surprise_ratio: float
    own_component_points: float
    benchmark_divergence_ratio: float
    benchmark_component_points: float
    attention_score: int
    classification: str
    is_reversal: bool


def score_change(
    stock_return: float,
    benchmark_return: float,
    rolling_volatility: float,
    residual_volatility: float,
    trading_days: int,
    max_excursion_return: float,
) -> ScoreResult:
    residual = calculate_residual_return(stock_return, benchmark_return)
    own_expected = expected_gap_volatility(rolling_volatility, trading_days)
    residual_expected = expected_gap_volatility(residual_volatility, trading_days)
    own_ratio = stock_return / own_expected if own_expected else 0.0
    residual_ratio = benchmark_divergence_ratio(residual, residual_expected)
    own_points = component_points(own_ratio, OWN_WEIGHT, NORMALIZATION_CAP)
    benchmark_points = benchmark_component_points(residual_ratio)
    attention_score = round(own_points + benchmark_points)
    is_reversal = detect_reversal(max_excursion_return, stock_return, own_expected)
    classification = "NEEDS_ATTENTION" if attention_score >= ATTENTION_THRESHOLD or is_reversal else "ROUTINE"
    return ScoreResult(
        stock_return=stock_return,
        benchmark_return=benchmark_return,
        residual_return=residual,
        expected_gap_volatility=own_expected,
        expected_residual_gap_volatility=residual_expected,
        own_surprise_ratio=own_ratio,
        own_component_points=own_points,
        benchmark_divergence_ratio=residual_ratio,
        benchmark_component_points=benchmark_points,
        attention_score=attention_score,
        classification=classification,
        is_reversal=is_reversal,
    )
