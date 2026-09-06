from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError

from demo.services import reset_demo
from market.constants import MAX_REPLAY_INDEX
from market.generator import reset_market_data
from market.models import MarketObservation, ReplayState
from market.services import advance_replay, get_replay_state


class ReplayTests(TestCase):
    def test_deterministic_reset(self):
        reset_market_data()
        advance_replay(1)
        first = list(MarketObservation.objects.filter(as_of=ReplayState.objects.first().current_as_of).order_by("symbol", "provider").values_list("symbol", "provider", "price"))
        reset_market_data()
        advance_replay(1)
        second = list(MarketObservation.objects.filter(as_of=ReplayState.objects.first().current_as_of).order_by("symbol", "provider").values_list("symbol", "provider", "price"))
        self.assertEqual(first, second)

    def test_replay_cannot_exceed_maximum(self):
        reset_market_data()
        advance_replay(99)
        self.assertEqual(get_replay_state().current_index, MAX_REPLAY_INDEX)

    def test_reset_leaves_clean_initial_state(self):
        reset_demo()
        advance_replay(2)
        reset_demo()
        state = get_replay_state()
        self.assertEqual(state.current_index, 0)
        self.assertEqual(ReplayState.objects.count(), 1)


class ReplaySingletonTransactionTests(TransactionTestCase):
    def test_replay_state_singleton(self):
        reset_market_data()
        with self.assertRaises(IntegrityError):
            ReplayState.objects.create(current_index=2, current_as_of=get_replay_state().current_as_of)
        self.assertEqual(ReplayState.objects.count(), 1)
