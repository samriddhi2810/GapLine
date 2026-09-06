from django.contrib.auth import get_user_model

from checkpoints.services import mark_understood
from demo.services import seed_demo
from market.services import advance_replay
from watchlists.models import WatchlistItem


def seeded_user(username="demo"):
    seed_demo()
    return get_user_model().objects.get(username=username)


def mark_all_understood(user):
    for item in WatchlistItem.objects.filter(watchlist__user=user):
        mark_understood(user, item)


def advance_after_marking(user):
    mark_all_understood(user)
    advance_replay(1)
