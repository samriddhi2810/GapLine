from __future__ import annotations

from django.db import transaction

from market.constants import SUPPORTED_SYMBOLS, SYMBOL_BENCHMARKS
from .models import Watchlist, WatchlistItem


def get_or_create_default_watchlist(user, name: str = "Demo Watchlist") -> Watchlist:
    watchlist, _ = Watchlist.objects.get_or_create(user=user, name=name)
    return watchlist


@transaction.atomic
def add_stock(user, watchlist: Watchlist, symbol: str) -> tuple[WatchlistItem, bool]:
    if watchlist.user_id != user.id:
        raise PermissionError("Watchlist does not belong to this user.")
    normalized = symbol.upper().strip()
    if normalized not in SUPPORTED_SYMBOLS:
        raise ValueError("Unsupported symbol.")
    item, created = WatchlistItem.objects.get_or_create(
        watchlist=watchlist,
        symbol=normalized,
        defaults={"benchmark_symbol": SYMBOL_BENCHMARKS[normalized]},
    )
    return item, created


@transaction.atomic
def remove_stock(user, item: WatchlistItem) -> None:
    if item.watchlist.user_id != user.id:
        raise PermissionError("Watchlist item does not belong to this user.")
    item.delete()
