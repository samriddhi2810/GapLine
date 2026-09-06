from django.db import models
from django.utils import timezone


class MarketObservation(models.Model):
    symbol = models.CharField(max_length=20)
    provider = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=14, decimal_places=4)
    as_of = models.DateTimeField()
    received_at = models.DateTimeField()
    quality_status = models.CharField(max_length=30, default="FRESH")
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["symbol", "as_of"])]

    def __str__(self) -> str:
        return f"{self.symbol} {self.price} @ {self.as_of}"


class MarketBar(models.Model):
    symbol = models.CharField(max_length=20)
    as_of = models.DateTimeField()
    close = models.DecimalField(max_digits=14, decimal_places=4)
    provider = models.CharField(max_length=60, default="DemoReplayProvider")
    is_benchmark = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["symbol", "as_of", "provider"], name="unique_bar_symbol_asof_provider")]
        indexes = [models.Index(fields=["symbol", "as_of"])]


class SymbolStatistic(models.Model):
    symbol = models.CharField(max_length=20)
    as_of = models.DateTimeField()
    rolling_20d_volatility = models.FloatField()
    benchmark_symbol = models.CharField(max_length=20)
    residual_20d_volatility = models.FloatField()
    calculated_at = models.DateTimeField(auto_now_add=True)


class DataIncident(models.Model):
    DELAYED = "DELAYED"
    CONFLICT = "CONFLICT"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    MISSING_INTERVAL = "MISSING_INTERVAL"
    MALFORMED = "MALFORMED"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    TYPES = [(value, value.replace("_", " ").title()) for value in [DELAYED, CONFLICT, OUT_OF_ORDER, MISSING_INTERVAL, MALFORMED, CORPORATE_ACTION]]

    symbol = models.CharField(max_length=20)
    incident_type = models.CharField(max_length=40, choices=TYPES)
    description = models.TextField()
    as_of = models.DateTimeField(null=True, blank=True)
    detected_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


class ReplayState(models.Model):
    singleton_enforcer = models.BooleanField(default=True, unique=True, editable=False)
    current_index = models.PositiveIntegerField(default=0)
    current_as_of = models.DateTimeField()
    scenario_version = models.CharField(max_length=40, default="gapline-demo-v1")
    updated_at = models.DateTimeField(auto_now=True)

# Create your models here.
