from django.contrib.auth import get_user_model
from django.test import TestCase

from market.generator import reset_market_data
from watchlists.models import WatchlistItem
from watchlists.services import add_stock, get_or_create_default_watchlist


class WatchlistTests(TestCase):
    def test_duplicate_stock_addition_is_idempotent(self):
        reset_market_data()
        user = get_user_model().objects.create_user("u", password="p")
        watchlist = get_or_create_default_watchlist(user)
        add_stock(user, watchlist, "INFY")
        add_stock(user, watchlist, "INFY")
        self.assertEqual(WatchlistItem.objects.filter(watchlist=watchlist, symbol="INFY").count(), 1)
