from decimal import Decimal

from django.test import TestCase

from checkpoints.services import mark_understood
from market.constants import PROVIDER_CONFLICT, PROVIDER_REPLAY
from market.models import DataIncident, MarketBar, MarketObservation
from market.generator import replay_as_of
from market.services import advance_replay, get_latest_observation, get_replay_state, provider_conflict, record_observation
from receipts.services import generate_receipt
from tests.helpers import seeded_user
from watchlists.models import WatchlistItem


class DataQualityTests(TestCase):
    def test_tcs_routine_fixture(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        advance_replay(1)
        self.assertEqual(generate_receipt(user, item).classification, "ROUTINE")

    def test_infy_attention_fixture(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        mark_understood(user, item)
        advance_replay(1)
        self.assertEqual(generate_receipt(user, item).classification, "NEEDS_ATTENTION")

    def test_delayed_data(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="HDFCBANK")
        mark_understood(user, item)
        advance_replay(1)
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.quality_status, "DELAYED")
        self.assertEqual(receipt.classification, "VERIFY_DATA")
        self.assertIsNone(receipt.attention_score)

    def test_provider_conflict(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="RELIANCE")
        mark_understood(user, item)
        advance_replay(1)
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.quality_status, "CONFLICTING")
        self.assertEqual(receipt.classification, "VERIFY_DATA")
        self.assertIsNone(receipt.attention_score)
        self.assertGreaterEqual(MarketObservation.objects.filter(symbol="RELIANCE", as_of=get_replay_state().current_as_of).count(), 2)

    def test_out_of_order_observation(self):
        user = seeded_user()
        state = get_replay_state()
        record_observation("INFY", PROVIDER_REPLAY, Decimal("10"), state.current_as_of, state.current_as_of)
        record_observation("INFY", PROVIDER_REPLAY, Decimal("9"), state.current_as_of.replace(day=state.current_as_of.day - 1), state.current_as_of)
        self.assertTrue(DataIncident.objects.filter(symbol="INFY", incident_type=DataIncident.OUT_OF_ORDER).exists())
        self.assertEqual(get_latest_observation("INFY", state).price, Decimal("10.0000"))

    def test_missing_interval(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="ICICIBANK")
        mark_understood(user, item)
        advance_replay(1)
        MarketBar.objects.filter(symbol="ICICIBANK", as_of=get_replay_state().current_as_of).delete()
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")

    def test_missing_one_intermediate_interval(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        advance_replay(3)
        MarketBar.objects.filter(symbol="TCS", as_of=replay_as_of(2)).delete()
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")
        self.assertEqual(receipt.quality_status, "MISSING_INTERVAL")

    def test_malformed_data(self):
        user = seeded_user()
        state = get_replay_state()
        self.assertIsNone(record_observation("INFY", PROVIDER_REPLAY, Decimal("-1"), state.current_as_of, state.current_as_of))
        self.assertTrue(DataIncident.objects.filter(symbol="INFY", incident_type=DataIncident.MALFORMED).exists())

    def test_insufficient_history(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        MarketBar.objects.filter(symbol="TCS").delete()
        advance_replay(1)
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")

    def test_observation_received_after_replay_is_not_visible(self):
        user = seeded_user()
        state = get_replay_state()
        future_received = replay_as_of(1)
        record_observation("INFY", PROVIDER_REPLAY, Decimal("9999"), state.current_as_of, future_received)
        self.assertNotEqual(get_latest_observation("INFY", state).price, Decimal("9999.0000"))

    def test_old_provider_quote_is_not_current_conflict(self):
        user = seeded_user()
        state = get_replay_state()
        old_as_of = replay_as_of(-1)
        MarketObservation.objects.create(symbol="TCS", provider=PROVIDER_CONFLICT, price=Decimal("9999"), as_of=old_as_of, received_at=state.current_as_of, quality_status="CONFLICTING")
        self.assertFalse(provider_conflict("TCS", state, replay_as_of(0)))

    def test_bad_benchmark_data_suppresses_score(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        mark_understood(user, item)
        advance_replay(1)
        obs = MarketObservation.objects.filter(symbol="NIFTYIT", as_of=get_replay_state().current_as_of).first()
        obs.quality_status = "DELAYED"
        obs.save()
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")
        self.assertIn("Benchmark NIFTYIT", receipt.explanation)

    def test_historical_timestamp_mismatch_suppresses_score(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="TCS")
        mark_understood(user, item)
        MarketBar.objects.filter(symbol="NIFTYIT", as_of=replay_as_of(-3)).delete()
        advance_replay(1)
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")

    def test_corporate_action(self):
        user = seeded_user()
        item = WatchlistItem.objects.get(watchlist__user=user, symbol="INFY")
        mark_understood(user, item)
        advance_replay(1)
        obs = MarketObservation.objects.filter(symbol="INFY", as_of=get_replay_state().current_as_of).first()
        obs.quality_status = "CORPORATE_ACTION"
        obs.save()
        receipt = generate_receipt(user, item)
        self.assertEqual(receipt.classification, "VERIFY_DATA")
