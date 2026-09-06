from django.conf import settings
from django.db import models


class ChangeReceipt(models.Model):
    ROUTINE = "ROUTINE"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    VERIFY_DATA = "VERIFY_DATA"
    CLASSIFICATIONS = [(ROUTINE, "Routine"), (NEEDS_ATTENTION, "Needs Attention"), (VERIFY_DATA, "Verify Data")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="change_receipts")
    watchlist_item = models.ForeignKey("watchlists.WatchlistItem", on_delete=models.CASCADE, related_name="receipts")
    checkpoint = models.ForeignKey("checkpoints.ItemCheckpoint", on_delete=models.RESTRICT, related_name="receipts")
    symbol = models.CharField(max_length=20)
    benchmark_symbol = models.CharField(max_length=20)
    checkpoint_price = models.DecimalField(max_digits=14, decimal_places=4)
    current_price = models.DecimalField(max_digits=14, decimal_places=4)
    checkpoint_as_of = models.DateTimeField()
    current_as_of = models.DateTimeField()
    current_received_at = models.DateTimeField()
    benchmark_checkpoint_price = models.DecimalField(max_digits=14, decimal_places=4)
    benchmark_current_price = models.DecimalField(max_digits=14, decimal_places=4)
    stock_return = models.FloatField(default=0)
    benchmark_return = models.FloatField(default=0)
    residual_return = models.FloatField(default=0)
    rolling_volatility = models.FloatField(default=0)
    expected_gap_volatility = models.FloatField(default=0)
    max_excursion_return = models.FloatField(default=0)
    own_surprise_ratio = models.FloatField(default=0)
    own_component_points = models.FloatField(default=0)
    residual_volatility = models.FloatField(default=0)
    expected_residual_gap_volatility = models.FloatField(default=0)
    benchmark_divergence_ratio = models.FloatField(default=0)
    benchmark_component_points = models.FloatField(default=0)
    attention_score = models.PositiveIntegerField(null=True, blank=True)
    classification = models.CharField(max_length=30, choices=CLASSIFICATIONS)
    is_reversal = models.BooleanField(default=False)
    quality_status = models.CharField(max_length=30, default="FRESH")
    explanation = models.TextField()
    replay_index = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "watchlist_item", "checkpoint", "replay_index"], name="unique_receipt_for_checkpoint_replay")
        ]
        indexes = [models.Index(fields=["user", "watchlist_item", "replay_index"])]

# Create your models here.
