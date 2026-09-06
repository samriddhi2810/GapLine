from django.conf import settings
from django.db import models


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlists")
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.user})"


class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name="items")
    symbol = models.CharField(max_length=20)
    benchmark_symbol = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["watchlist", "symbol"], name="unique_symbol_per_watchlist")
        ]
        indexes = [models.Index(fields=["watchlist", "symbol"])]

    def __str__(self) -> str:
        return f"{self.symbol} vs {self.benchmark_symbol}"

# Create your models here.
