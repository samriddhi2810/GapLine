from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from scoring.constants import PROVIDER_CONFLICT_TOLERANCE
from .constants import MAX_REPLAY_INDEX, PROVIDER_REPLAY, REPLAY_START, SYMBOL_BENCHMARKS, TRADING_DAY
from .models import DataIncident, MarketObservation, ReplayState


def get_replay_state() -> ReplayState:
    state = ReplayState.objects.order_by("id").first()
    if state is None:
        state = ReplayState.objects.create(current_index=0, current_as_of=REPLAY_START)
    ReplayState.objects.exclude(id=state.id).delete()
    return state


def get_replay_state_for_update() -> ReplayState:
    state = get_replay_state()
    return ReplayState.objects.select_for_update().get(id=state.id)


def get_latest_observation(symbol: str, state: ReplayState, provider: str = PROVIDER_REPLAY) -> MarketObservation | None:
    return (
        MarketObservation.objects.filter(
            symbol=symbol,
            provider=provider,
            as_of__lte=state.current_as_of,
            received_at__lte=state.current_as_of,
        )
        .order_by("-as_of", "-received_at", "-id")
        .first()
    )


def get_benchmark_symbol(symbol: str) -> str:
    return SYMBOL_BENCHMARKS[symbol]


@transaction.atomic
def advance_replay(days: int = 1) -> ReplayState:
    state = get_replay_state_for_update()
    state.current_index = min(state.current_index + days, MAX_REPLAY_INDEX)
    state.current_as_of = REPLAY_START + TRADING_DAY * state.current_index
    state.save(update_fields=["current_index", "current_as_of", "updated_at"])
    return state


def record_observation(symbol: str, provider: str, price: Decimal, as_of, received_at, quality_status: str = "FRESH") -> MarketObservation | None:
    if price <= 0:
        DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.MALFORMED, description="Non-positive price rejected.", as_of=as_of)
        return None
    latest = MarketObservation.objects.filter(symbol=symbol, provider=provider).order_by("-as_of").first()
    if latest and as_of < latest.as_of:
        DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.OUT_OF_ORDER, description="Older as_of arrived after a newer value.", as_of=as_of)
    return MarketObservation.objects.create(symbol=symbol, provider=provider, price=price, as_of=as_of, received_at=received_at, quality_status=quality_status)


def provider_conflict(symbol: str, state: ReplayState, reference_as_of=None) -> bool:
    reference_as_of = reference_as_of or (get_latest_observation(symbol, state).as_of if get_latest_observation(symbol, state) else None)
    if reference_as_of is None:
        return False
    observations = list(
        MarketObservation.objects.filter(
            symbol=symbol,
            as_of=reference_as_of,
            received_at__lte=state.current_as_of,
        ).order_by("provider", "-received_at", "-id")
    )
    latest_by_provider = {}
    for observation in observations:
        latest_by_provider.setdefault(observation.provider, observation)
    if len(latest_by_provider) < 2:
        return False
    prices = [float(observation.price) for observation in latest_by_provider.values()]
    if min(prices) <= 0:
        return False
    return (max(prices) - min(prices)) / min(prices) > PROVIDER_CONFLICT_TOLERANCE
