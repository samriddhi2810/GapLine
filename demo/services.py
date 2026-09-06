from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction

from checkpoints.models import ItemCheckpoint
from market.generator import reset_market_data
from market.services import advance_replay, get_replay_state_for_update
from receipts.models import ChangeReceipt
from watchlists.models import Watchlist, WatchlistItem
from watchlists.services import add_stock, get_or_create_default_watchlist
from market.constants import SUPPORTED_SYMBOLS

DEMO_PASSWORD = "gapline-demo"
SECOND_PASSWORD = "gapline-second"


@transaction.atomic
def seed_demo() -> None:
    get_replay_state_for_update()
    ChangeReceipt.objects.all().delete()
    ItemCheckpoint.objects.all().delete()
    WatchlistItem.objects.all().delete()
    Watchlist.objects.all().delete()
    reset_market_data()
    User = get_user_model()
    demo_user, _ = User.objects.get_or_create(username="demo", defaults={"email": "demo@gapline.local"})
    demo_user.email = "demo@gapline.local"
    demo_user.is_staff = True
    demo_user.set_password(DEMO_PASSWORD)
    demo_user.save()
    second_user, _ = User.objects.get_or_create(username="second", defaults={"email": "second@gapline.local"})
    second_user.email = "second@gapline.local"
    second_user.is_staff = False
    second_user.set_password(SECOND_PASSWORD)
    second_user.save()
    for user in (demo_user, second_user):
        watchlist = get_or_create_default_watchlist(user)
        for symbol in SUPPORTED_SYMBOLS:
            add_stock(user, watchlist, symbol)


@transaction.atomic
def reset_demo() -> None:
    seed_demo()


def advance_demo(days: int = 1):
    return advance_replay(days)
