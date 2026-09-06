from __future__ import annotations

from django.db import IntegrityError, transaction

from market.data_quality import validate_current_observation
from market.services import get_benchmark_symbol, get_latest_observation, get_replay_state
from .models import ItemCheckpoint


class CheckpointUnavailable(Exception):
    pass


@transaction.atomic
def mark_understood(user, watchlist_item, state=None) -> ItemCheckpoint:
    if watchlist_item.watchlist.user_id != user.id:
        raise PermissionError("Cannot checkpoint another user's watchlist item.")
    state = state or get_replay_state()
    observation = get_latest_observation(watchlist_item.symbol, state)
    benchmark_observation = get_latest_observation(get_benchmark_symbol(watchlist_item.symbol), state)
    stock_quality = validate_current_observation(watchlist_item.symbol, observation, state, "Stock")
    if not stock_quality.can_score:
        raise CheckpointUnavailable(stock_quality.explanation)
    benchmark_quality = validate_current_observation(watchlist_item.benchmark_symbol, benchmark_observation, state, f"Benchmark {watchlist_item.benchmark_symbol}")
    if not benchmark_quality.can_score:
        raise CheckpointUnavailable(benchmark_quality.explanation)
    if observation.as_of != benchmark_observation.as_of:
        raise CheckpointUnavailable("Stock and benchmark observations are not aligned.")
    try:
        checkpoint, _ = ItemCheckpoint.objects.get_or_create(
            user=user,
            watchlist_item=watchlist_item,
            replay_index=state.current_index,
            defaults={
                "symbol": watchlist_item.symbol,
                "checkpoint_price": observation.price,
                "benchmark_price": benchmark_observation.price,
                "checkpoint_as_of": observation.as_of,
            },
        )
    except IntegrityError:
        checkpoint = ItemCheckpoint.objects.get(user=user, watchlist_item=watchlist_item, replay_index=state.current_index)
    return checkpoint
