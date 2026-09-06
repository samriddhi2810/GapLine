from django.test import TestCase

from checkpoints.models import ItemCheckpoint
from checkpoints.services import mark_understood
from receipts.services import generate_receipt
from tests.helpers import seeded_user
from watchlists.models import WatchlistItem


class UserIsolationTests(TestCase):
    def test_user_data_is_isolated(self):
        user_a = seeded_user("demo")
        user_b = seeded_user("second")
        item_a = WatchlistItem.objects.get(watchlist__user=user_a, symbol="INFY")
        item_b = WatchlistItem.objects.get(watchlist__user=user_b, symbol="INFY")
        mark_understood(user_a, item_a)
        self.assertFalse(ItemCheckpoint.objects.filter(user=user_b, watchlist_item=item_b).exists())
        self.client.login(username="second", password="gapline-second")
        self.assertEqual(self.client.post(f"/watchlists/api/items/{item_a.id}/mark-understood/", content_type="application/json").status_code, 404)
        receipt = generate_receipt(user_a, item_a)
        self.assertEqual(self.client.get(f"/receipts/{receipt.id}/").status_code, 404)

    def test_global_replay_controls_are_staff_only(self):
        seeded_user("demo")
        seeded_user("second")
        self.client.login(username="demo", password="gapline-demo")
        self.assertEqual(self.client.post("/demo/api/advance/", content_type="application/json").status_code, 200)
        self.assertEqual(self.client.post("/demo/api/reset/", content_type="application/json").status_code, 200)
        self.client.logout()
        self.client.login(username="second", password="gapline-second")
        self.assertEqual(self.client.post("/demo/api/advance/", content_type="application/json").status_code, 403)
        self.assertEqual(self.client.post("/demo/api/reset/", content_type="application/json").status_code, 403)
        self.assertEqual(self.client.get("/demo/controls/").status_code, 403)
