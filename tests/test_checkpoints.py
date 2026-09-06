from django.test import TestCase

from checkpoints.models import ItemCheckpoint
from checkpoints.services import CheckpointUnavailable, mark_understood
from market.models import MarketObservation
from market.generator import replay_as_of
from market.services import advance_replay
from receipts.services import generate_receipt
from tests.helpers import seeded_user
from watchlists.models import WatchlistItem


class CheckpointTests(TestCase):
    def test_checkpoint_persistence_and_append_only(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        first = mark_understood(user, item)
        self.assertTrue(ItemCheckpoint.objects.filter(id=first.id).exists())
        advance_replay(1)
        second = mark_understood(user, item)
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(ItemCheckpoint.objects.filter(user=user, watchlist_item=item).count(), 2)

    def test_page_view_does_not_checkpoint(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        advance_replay(1)
        receipt = generate_receipt(user, item)
        self.client.login(username="demo", password="gapline-demo")
        before = ItemCheckpoint.objects.count()
        self.client.get("/dashboard/")
        self.client.get(f"/receipts/{receipt.id}/")
        self.client.get("/dashboard/")
        self.assertEqual(ItemCheckpoint.objects.count(), before)

    def test_explicit_checkpoint_only(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        self.client.login(username="demo", password="gapline-demo")
        advance_replay(1)
        self.client.get("/dashboard/")
        self.assertEqual(ItemCheckpoint.objects.filter(user=user, watchlist_item=item).count(), 0)
        self.client.post(f"/watchlists/api/items/{item.id}/mark-understood/", content_type="application/json")
        self.assertEqual(ItemCheckpoint.objects.filter(user=user, watchlist_item=item).count(), 1)

    def test_same_replay_mark_understood_is_idempotent(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        first = mark_understood(user, item)
        second = mark_understood(user, item)
        self.assertEqual(first.id, second.id)
        self.assertEqual(ItemCheckpoint.objects.filter(user=user, watchlist_item=item, replay_index=0).count(), 1)

    def test_missing_observation_rejected(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        MarketObservation.objects.filter(symbol="TCS").delete()
        with self.assertRaises(CheckpointUnavailable):
            mark_understood(user, item)

    def test_stale_stock_rejected(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="HDFCBANK")
        advance_replay(1)
        with self.assertRaises(CheckpointUnavailable):
            mark_understood(user, item)

    def test_stale_benchmark_rejected(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        obs = MarketObservation.objects.get(symbol="NIFTYIT", as_of=replay_as_of(0))
        obs.quality_status = "DELAYED"
        obs.save()
        with self.assertRaises(CheckpointUnavailable):
            mark_understood(user, item)

    def test_timestamp_mismatch_rejected(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        obs = MarketObservation.objects.get(symbol="TCS", as_of=replay_as_of(0))
        obs.as_of = obs.as_of.replace(day=obs.as_of.day - 1)
        obs.save()
        with self.assertRaises(CheckpointUnavailable):
            mark_understood(user, item)

    def test_current_provider_conflict_rejected(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="RELIANCE")
        advance_replay(1)
        with self.assertRaises(CheckpointUnavailable):
            mark_understood(user, item)
