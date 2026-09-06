from __future__ import annotations

from dataclasses import dataclass

from scoring.constants import FRESHNESS_THRESHOLD_MINUTES, ROLLING_WINDOW_DAYS
from .generator import replay_as_of
from .models import DataIncident, MarketBar
from .services import provider_conflict


@dataclass(frozen=True)
class QualityResult:
    status: str
    explanation: str
    can_score: bool


def validate_current_observation(symbol: str, observation, state, label: str = "Stock") -> QualityResult:
    if observation is None:
        DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.MISSING_INTERVAL, description="No current observation available.", as_of=state.current_as_of)
        return QualityResult("MISSING_INTERVAL", f"{label} data is missing.", False)
    if observation.price <= 0:
        DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.MALFORMED, description="Non-positive market price.", as_of=observation.as_of)
        return QualityResult("MALFORMED", f"{label} data is malformed.", False)
    if observation.received_at > state.current_as_of:
        return QualityResult("MISSING_INTERVAL", f"{label} data is not available yet.", False)
    if observation.quality_status == "CORPORATE_ACTION":
        DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.CORPORATE_ACTION, description="Corporate action fixture blocks scoring.", as_of=observation.as_of)
        return QualityResult("CORPORATE_ACTION", f"{label} data has a corporate action requiring verification.", False)
    age_minutes = (state.current_as_of - observation.received_at).total_seconds() / 60
    if observation.quality_status == "DELAYED" or age_minutes > FRESHNESS_THRESHOLD_MINUTES:
        DataIncident.objects.get_or_create(symbol=symbol, incident_type=DataIncident.DELAYED, as_of=observation.as_of, defaults={"description": "Latest observation is stale for replay time."})
        return QualityResult("DELAYED", f"{label} data is stale.", False)
    if provider_conflict(symbol, state, observation.as_of):
        DataIncident.objects.get_or_create(symbol=symbol, incident_type=DataIncident.CONFLICT, as_of=observation.as_of, defaults={"description": "Providers disagree beyond tolerance."})
        return QualityResult("CONFLICTING", f"{label} provider data is conflicting.", False)
    return QualityResult("FRESH", f"{label} data passed current checks.", True)


def evaluate_data_quality(symbol: str, observation, state, checkpoint=None, label: str = "Stock") -> QualityResult:
    current = validate_current_observation(symbol, observation, state, label)
    if not current.can_score:
        return current
    checkpoint_as_of = checkpoint.checkpoint_as_of if checkpoint else None
    if checkpoint_as_of:
        expected = [replay_as_of(index) for index in range(checkpoint.replay_index + 1, state.current_index + 1)]
        existing = set(MarketBar.objects.filter(symbol=symbol, as_of__in=expected).values_list("as_of", flat=True))
        if len(existing) != len(expected):
            DataIncident.objects.create(symbol=symbol, incident_type=DataIncident.MISSING_INTERVAL, description="Missing one or more replay bars in checkpoint gap.", as_of=state.current_as_of)
            return QualityResult("MISSING_INTERVAL", f"{label} has missing market intervals.", False)
    history = MarketBar.objects.filter(symbol=symbol, as_of__lt=observation.as_of).count()
    if history < ROLLING_WINDOW_DAYS:
        return QualityResult("INSUFFICIENT_HISTORY", f"{label} has fewer than 20 historical returns.", False)
    return QualityResult("FRESH", f"{label} data passed freshness and consistency checks.", True)
