from django.test import TestCase

from checkpoints.services import mark_understood
from market.services import advance_replay
from receipts.models import ChangeReceipt
from receipts.services import generate_receipt
from tests.helpers import seeded_user
from watchlists.models import WatchlistItem


class ReceiptTests(TestCase):
    def test_receipt_immutability(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        mark_understood(user, item)
        advance_replay(1)
        receipt = generate_receipt(user, item)
        snapshot = (receipt.current_price, receipt.attention_score, receipt.explanation)
        advance_replay(1)
        receipt.refresh_from_db()
        self.assertEqual((receipt.current_price, receipt.attention_score, receipt.explanation), snapshot)

    def test_no_duplicate_receipt(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        advance_replay(1)
        first = generate_receipt(user, item)
        second = generate_receipt(user, item)
        self.assertEqual(first.id, second.id)
        self.assertEqual(ChangeReceipt.objects.filter(user=user, watchlist_item=item).count(), 1)

    def test_watchlist_item_with_receipt_can_be_deleted(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        advance_replay(1)
        generate_receipt(user, item)
        item.delete()
        self.assertFalse(WatchlistItem.objects.filter(id=item.id).exists())
