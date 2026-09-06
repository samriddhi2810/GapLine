from __future__ import annotations

from checkpoints.selectors import latest_checkpoint
from market.services import get_replay_state
from receipts.services import generate_receipt
from watchlists.services import get_or_create_default_watchlist


def dashboard_context(user, state=None) -> dict:
    state = state or get_replay_state()
    watchlist = get_or_create_default_watchlist(user)
    items = watchlist.items.select_related("watchlist").order_by("symbol")
    receipts = []
    no_checkpoint = []
    for item in items:
        checkpoint = latest_checkpoint(user, item)
        if not checkpoint:
            no_checkpoint.append(item)
            continue
        receipt = generate_receipt(user, item, state=state)
        if receipt:
            receipts.append(receipt)
    attention = [r for r in receipts if r.classification == "NEEDS_ATTENTION"]
    verify = [r for r in receipts if r.classification == "VERIFY_DATA"]
    routine = [r for r in receipts if r.classification == "ROUTINE"]
    return {
        "watchlist": watchlist,
        "items": items,
        "receipts": receipts,
        "attention": sorted(attention, key=lambda r: r.attention_score or 0, reverse=True),
        "verify": verify,
        "routine": routine,
        "no_checkpoint": no_checkpoint,
        "counts": {"attention": len(attention), "verify": len(verify), "routine": len(routine), "no_checkpoint": len(no_checkpoint)},
        "replay_state": state,
    }
