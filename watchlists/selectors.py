from __future__ import annotations

from .models import Watchlist


def user_watchlists(user):
    return Watchlist.objects.filter(user=user).prefetch_related("items")


def get_user_watchlist(user, watchlist_id: int) -> Watchlist:
    return Watchlist.objects.prefetch_related("items").get(id=watchlist_id, user=user)
