from __future__ import annotations

from rest_framework import serializers

from market.constants import SUPPORTED_SYMBOLS
from .models import Watchlist, WatchlistItem


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ["id", "name", "created_at", "updated_at"]


class AddStockSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20)

    def validate_symbol(self, value: str) -> str:
        symbol = value.upper().strip()
        if symbol not in SUPPORTED_SYMBOLS:
            raise serializers.ValidationError("Unsupported symbol.")
        return symbol


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ["id", "symbol", "benchmark_symbol", "created_at"]
