from __future__ import annotations

from django.db import transaction

from checkpoints.selectors import latest_checkpoint
from market.constants import PROVIDER_REPLAY
from market.data_quality import evaluate_data_quality
from market.models import MarketBar
from market.services import get_latest_observation, get_replay_state
from scoring.constants import ATTENTION_THRESHOLD, ROLLING_WINDOW_DAYS
from scoring.engine import score_change
from scoring.volatility import calculate_returns, sample_standard_deviation
from .models import ChangeReceipt


def simple_return(start, end) -> float:
    return float(end) / float(start) - 1 if float(start) > 0 else 0.0


def _historical_bars(symbol: str, before_as_of, limit: int = ROLLING_WINDOW_DAYS + 1) -> list:
    return list(
        MarketBar.objects.filter(symbol=symbol, provider=PROVIDER_REPLAY, as_of__lt=before_as_of)
        .order_by("-as_of")
        .values("as_of", "close")[:limit]
    )[::-1]


def _gap_prices(symbol: str, start, end) -> list:
    return list(
        MarketBar.objects.filter(symbol=symbol, provider=PROVIDER_REPLAY, as_of__gte=start, as_of__lte=end)
        .order_by("as_of")
        .values_list("close", flat=True)
    )


def _create_receipt(defaults: dict) -> ChangeReceipt:
    identity = {
        "user": defaults.pop("user"),
        "watchlist_item": defaults.pop("watchlist_item"),
        "checkpoint": defaults.pop("checkpoint"),
        "replay_index": defaults.pop("replay_index"),
    }
    receipt, _ = ChangeReceipt.objects.get_or_create(**identity, defaults=defaults)
    return receipt


def _aligned_returns(stock_bars: list[dict], benchmark_bars: list[dict]) -> tuple[list[float], list[float]] | None:
    stock_by_time = {bar["as_of"]: bar["close"] for bar in stock_bars}
    benchmark_by_time = {bar["as_of"]: bar["close"] for bar in benchmark_bars}
    aligned_times = sorted(set(stock_by_time) & set(benchmark_by_time))
    if len(aligned_times) < ROLLING_WINDOW_DAYS + 1:
        return None
    aligned_times = aligned_times[-(ROLLING_WINDOW_DAYS + 1):]
    stock_prices = [stock_by_time[as_of] for as_of in aligned_times]
    benchmark_prices = [benchmark_by_time[as_of] for as_of in aligned_times]
    return calculate_returns(stock_prices), calculate_returns(benchmark_prices)


def generate_receipt(user, watchlist_item, state=None) -> ChangeReceipt | None:
    checkpoint = latest_checkpoint(user, watchlist_item)
    if checkpoint is None:
        return None
    return generate_receipt_for_checkpoint(user, watchlist_item, checkpoint, state=state)


@transaction.atomic
def generate_receipt_for_checkpoint(user, watchlist_item, checkpoint, state=None) -> ChangeReceipt:
    if watchlist_item.watchlist.user_id != user.id or checkpoint.user_id != user.id:
        raise PermissionError("Cannot generate receipt for another user's data.")
    state = state or get_replay_state()
    current = get_latest_observation(watchlist_item.symbol, state)
    benchmark_current = get_latest_observation(watchlist_item.benchmark_symbol, state)
    stock_quality = evaluate_data_quality(watchlist_item.symbol, current, state, checkpoint, "Stock")
    benchmark_quality = evaluate_data_quality(watchlist_item.benchmark_symbol, benchmark_current, state, checkpoint, f"Benchmark {watchlist_item.benchmark_symbol}")
    quality = stock_quality if not stock_quality.can_score else benchmark_quality

    defaults = {
        "user": user,
        "watchlist_item": watchlist_item,
        "checkpoint": checkpoint,
        "symbol": watchlist_item.symbol,
        "benchmark_symbol": watchlist_item.benchmark_symbol,
        "checkpoint_price": checkpoint.checkpoint_price,
        "current_price": current.price if current else checkpoint.checkpoint_price,
        "checkpoint_as_of": checkpoint.checkpoint_as_of,
        "current_as_of": current.as_of if current else checkpoint.checkpoint_as_of,
        "current_received_at": current.received_at if current else checkpoint.checkpoint_as_of,
        "benchmark_checkpoint_price": checkpoint.benchmark_price,
        "benchmark_current_price": benchmark_current.price if benchmark_current else checkpoint.benchmark_price,
        "classification": "VERIFY_DATA" if not quality.can_score else "ROUTINE",
        "quality_status": quality.status,
        "attention_score": None if not quality.can_score else 0,
        "explanation": quality.explanation,
        "replay_index": state.current_index,
    }
    if not quality.can_score:
        return _create_receipt(defaults)

    stock_history = _historical_bars(watchlist_item.symbol, checkpoint.checkpoint_as_of)
    benchmark_history = _historical_bars(watchlist_item.benchmark_symbol, checkpoint.checkpoint_as_of)
    aligned = _aligned_returns(stock_history, benchmark_history)
    if not aligned:
        defaults.update({"classification": "VERIFY_DATA", "quality_status": "INSUFFICIENT_HISTORY", "attention_score": None, "explanation": "Insufficient history for a 20-day baseline."})
        return _create_receipt(defaults)
    stock_returns, benchmark_returns = aligned

    residual_returns = [s - b for s, b in zip(stock_returns, benchmark_returns)]
    stock_return = simple_return(checkpoint.checkpoint_price, current.price)
    benchmark_return = simple_return(checkpoint.benchmark_price, benchmark_current.price)
    gap_prices = _gap_prices(watchlist_item.symbol, checkpoint.checkpoint_as_of, current.as_of)
    excursion = max([abs(simple_return(checkpoint.checkpoint_price, price)) for price in gap_prices] or [abs(stock_return)])
    trading_days = max(state.current_index - checkpoint.replay_index, 1)
    result = score_change(
        stock_return=stock_return,
        benchmark_return=benchmark_return,
        rolling_volatility=sample_standard_deviation(stock_returns),
        residual_volatility=sample_standard_deviation(residual_returns),
        trading_days=trading_days,
        max_excursion_return=excursion,
    )
    defaults.update(
        {
            "stock_return": result.stock_return,
            "benchmark_return": result.benchmark_return,
            "residual_return": result.residual_return,
            "rolling_volatility": sample_standard_deviation(stock_returns),
            "expected_gap_volatility": result.expected_gap_volatility,
            "max_excursion_return": excursion,
            "own_surprise_ratio": result.own_surprise_ratio,
            "own_component_points": result.own_component_points,
            "residual_volatility": sample_standard_deviation(residual_returns),
            "expected_residual_gap_volatility": result.expected_residual_gap_volatility,
            "benchmark_divergence_ratio": result.benchmark_divergence_ratio,
            "benchmark_component_points": result.benchmark_component_points,
            "attention_score": result.attention_score,
            "classification": result.classification,
            "is_reversal": result.is_reversal,
            "quality_status": "FRESH",
            "explanation": (
                f"Own move {result.stock_return:.2%} vs expected {result.expected_gap_volatility:.2%}; "
                f"benchmark residual {result.residual_return:.2%} vs expected {result.expected_residual_gap_volatility:.2%}. "
                f"Score {result.attention_score}."
            ),
        }
    )
    if result.is_reversal and result.attention_score < ATTENTION_THRESHOLD:
        defaults["explanation"] = (
            "Surfaced because the stock made a large intragap move and sharply reversed. "
            f"Statistical attention score: {result.attention_score}. "
            f"Maximum excursion: {excursion:.2%}; final return: {result.stock_return:.2%}."
        )
    return _create_receipt(defaults)
