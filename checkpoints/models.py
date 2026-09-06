from django.conf import settings
from django.db import models


class ItemCheckpoint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_checkpoints")
    watchlist_item = models.ForeignKey("watchlists.WatchlistItem", on_delete=models.CASCADE, related_name="checkpoints")
    symbol = models.CharField(max_length=20)
    checkpoint_price = models.DecimalField(max_digits=14, decimal_places=4)
    benchmark_price = models.DecimalField(max_digits=14, decimal_places=4)
    checkpoint_as_of = models.DateTimeField()
    replay_index = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "watchlist_item", "replay_index"], name="unique_checkpoint_user_item_replay")
        ]
        indexes = [models.Index(fields=["user", "watchlist_item", "created_at"])]

    def __str__(self) -> str:
        return f"{self.symbol} checkpoint #{self.replay_index}"

# Create your models here.
