from __future__ import annotations

import random
from decimal import Decimal

from django.db import transaction

from market.constants import ALL_MARKET_SYMBOLS, BENCHMARK_SYMBOLS, DEMO_RANDOM_SEED, MAX_REPLAY_INDEX, PROVIDER_CONFLICT, PROVIDER_REPLAY, REPLAY_START, TRADING_DAY
from market.models import DataIncident, MarketBar, MarketObservation, ReplayState

BASE_PRICES = {
    "NIFTY50": Decimal("25000"),
    "NIFTYIT": Decimal("39000"),
    "NIFTYBANK": Decimal("52000"),
    "NIFTYAUTO": Decimal("22500"),
    "INFY": Decimal("1500"),
    "TCS": Decimal("4200"),
    "RELIANCE": Decimal("2900"),
    "HDFCBANK": Decimal("1640"),
    "ICICIBANK": Decimal("1200"),
    "TATAMOTORS": Decimal("980"),
}
SECTOR = {"NIFTYIT": "IT", "INFY": "IT", "TCS": "IT", "NIFTYBANK": "BANK", "HDFCBANK": "BANK", "ICICIBANK": "BANK", "NIFTYAUTO": "AUTO", "TATAMOTORS": "AUTO", "NIFTY50": "MARKET", "RELIANCE": "MARKET"}


def q(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"))


def replay_as_of(index: int):
    return REPLAY_START + TRADING_DAY * index


def scenario_return(symbol: str, step: int) -> float:
    table = {
        "NIFTYIT": [0.006, 0.004, 0.003, 0.002],
        "TCS": [0.0062, 0.0042, 0.0032, 0.0022],
        "INFY": [-0.055, -0.010, -0.004, 0.002],
        "NIFTY50": [0.003, 0.002, 0.002, 0.001],
        "RELIANCE": [0.004, 0.003, 0.002, 0.001],
        "NIFTYBANK": [0.002, 0.002, 0.002, 0.001],
        "HDFCBANK": [0.002, 0.002, 0.002, 0.001],
        "ICICIBANK": [0.003, 0.002, 0.002, 0.001],
        "NIFTYAUTO": [0.001, 0.001, 0.001, 0.001],
        "TATAMOTORS": [0.090, -0.070, -0.015, 0.000],
    }
    return table.get(symbol, [0.001])[min(step - 1, 3)]


def reset_market_data() -> ReplayState:
    MarketObservation.objects.all().delete()
    MarketBar.objects.all().delete()
    DataIncident.objects.all().delete()
    rng = random.Random(DEMO_RANDOM_SEED)
    prices = BASE_PRICES.copy()

    for idx in range(-21, 1):
        as_of = replay_as_of(idx)
        market_factor = rng.gauss(0.0005, 0.006)
        factors = {"IT": rng.gauss(0.0007, 0.008), "BANK": rng.gauss(0.0004, 0.006), "AUTO": rng.gauss(0.0006, 0.010), "MARKET": market_factor}
        for symbol in ALL_MARKET_SYMBOLS:
            sector = SECTOR[symbol]
            if idx < 0:
                noise = 0 if symbol in BENCHMARK_SYMBOLS else rng.gauss(0, 0.004)
                ret = 0.65 * market_factor + 0.55 * factors[sector] + noise
                prices[symbol] = q(prices[symbol] * q(1 + ret))
            is_benchmark = symbol in BENCHMARK_SYMBOLS
            MarketBar.objects.create(symbol=symbol, as_of=as_of, close=prices[symbol], provider=PROVIDER_REPLAY, is_benchmark=is_benchmark)
            MarketObservation.objects.create(symbol=symbol, provider=PROVIDER_REPLAY, price=prices[symbol], as_of=as_of, received_at=as_of, quality_status="FRESH")

    for step in range(1, MAX_REPLAY_INDEX + 1):
        as_of = replay_as_of(step)
        for symbol in ALL_MARKET_SYMBOLS:
            previous = prices[symbol]
            prices[symbol] = q(previous * q(1 + scenario_return(symbol, step)))
            MarketBar.objects.create(symbol=symbol, as_of=as_of, close=prices[symbol], provider=PROVIDER_REPLAY, is_benchmark=symbol in BENCHMARK_SYMBOLS)
            received = as_of
            quality = "FRESH"
            if symbol == "HDFCBANK" and step >= 1:
                received = replay_as_of(step + 1)
                quality = "DELAYED"
            MarketObservation.objects.create(symbol=symbol, provider=PROVIDER_REPLAY, price=prices[symbol], as_of=as_of, received_at=received, quality_status=quality)

    conflict_as_of = replay_as_of(1)
    replay_reliance = MarketObservation.objects.get(symbol="RELIANCE", provider=PROVIDER_REPLAY, as_of=conflict_as_of)
    MarketObservation.objects.create(symbol="RELIANCE", provider=PROVIDER_CONFLICT, price=q(replay_reliance.price * Decimal("1.05")), as_of=conflict_as_of, received_at=conflict_as_of, quality_status="CONFLICTING")
    DataIncident.objects.create(symbol="RELIANCE", incident_type=DataIncident.CONFLICT, description="Demo provider conflict exceeds tolerance.", as_of=conflict_as_of)
    state = ReplayState.objects.order_by("id").first()
    if state is None:
        state = ReplayState.objects.create(current_index=0, current_as_of=replay_as_of(0), singleton_enforcer=True)
    else:
        state.current_index = 0
        state.current_as_of = replay_as_of(0)
        state.singleton_enforcer = True
        state.save(update_fields=["current_index", "current_as_of", "singleton_enforcer", "updated_at"])
    ReplayState.objects.exclude(id=state.id).delete()
    return state
