from django.test import TestCase

from checkpoints.services import mark_understood
from market.services import advance_replay
from receipts.services import generate_receipt
from tests.helpers import seeded_user
from watchlists.models import WatchlistItem


class ReversalFixtureTests(TestCase):
    def test_tatamotors_reversal(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TATAMOTORS")
        mark_understood(user, item)
        advance_replay(3)
        receipt = generate_receipt(user, item)
        self.assertTrue(receipt.is_reversal)
        self.assertEqual(receipt.classification, "NEEDS_ATTENTION")
        self.assertIn("reversed", receipt.explanation.lower())
