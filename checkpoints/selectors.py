from __future__ import annotations

from .models import ItemCheckpoint


def latest_checkpoint(user, watchlist_item):
    return ItemCheckpoint.objects.filter(user=user, watchlist_item=watchlist_item).order_by("-replay_index", "-created_at").first()
