# Gapline Decisions

## Explicit checkpoint vs last-seen timestamp
Context: A page view does not mean the user understood market context.  
Decision: Only "Mark understood" creates an ItemCheckpoint.  
Reason: It gives the comparison a deliberate baseline.  
Trade-off: Users must take one extra explicit action.

## 20 trading-day window
Context: The product needs a compact volatility baseline.  
Decision: Use 21 closes to calculate 20 daily returns.  
Reason: It is understandable and enough for a hackathon demo.  
Trade-off: It is less stable than longer horizons.

## sqrt(D) volatility scaling
Context: Checkpoint gaps can span multiple replay days.  
Decision: Scale daily volatility by sqrt(days).  
Reason: It is a standard simple approximation for multi-day volatility.  
Trade-off: It assumes independent daily returns.

## Benchmark residual
Context: Broad market or sector moves can create false urgency.  
Decision: Compare stock return minus benchmark return.  
Reason: Residual movement better captures unusual stock-specific change.  
Trade-off: Benchmark choice matters.

## 45/55 weighting and threshold
Context: Own movement and benchmark divergence both matter.  
Decision: Allocate 45 points to own surprise, 55 to residual divergence, threshold at 60.  
Reason: Divergence gets slightly more weight because it filters market-wide movement.  
Trade-off: Weights are product choices, not statistical certainties.

## Reversal definition
Context: Final price can hide a large intragap move.  
Decision: Flag reversal when max excursion exceeds 2x expected volatility and final return is within 35% of excursion.  
Reason: It surfaces meaningful round trips without adding score.  
Trade-off: It depends on stored path data.

## Data quality before score
Context: Bad data can create false confidence.  
Decision: Gate delayed, conflicting, missing, malformed, corporate-action, and out-of-order data before scoring.  
Reason: Verify Data is more honest than a precise-looking bad score.  
Trade-off: Some items may be withheld until data is reliable.

## as_of vs received_at
Context: Arrival time and market truth time are different.  
Decision: Order market values by as_of and evaluate freshness against received_at.  
Reason: Late older data must not replace newer market truth.  
Trade-off: More fields and tests are required.

## Deterministic replay
Context: Hackathon demos need repeatability.  
Decision: Fixed seed, fixed clock, synthetic correlated factors.  
Reason: The same demo can be reset exactly.  
Trade-off: It is not live-market realism.

## Immutable receipts
Context: Explanations must remain auditable.  
Decision: Store a full calculation snapshot per checkpoint and replay index.  
Reason: Advancing replay cannot rewrite history.  
Trade-off: Receipts duplicate calculated values.

## Modular monolith, Django, MySQL, sessions
Context: The app is cohesive and user-state heavy.  
Decision: Use a Django modular monolith, Django ORM, MySQL, and Django sessions.  
Reason: This keeps delivery simple, secure, and GitHub-friendly.  
Trade-off: Scaling boundaries are logical rather than service-level.

## No Redis, Kafka, microservices, or WebSockets
Context: The core loop is request/response and deterministic.  
Decision: Exclude extra infrastructure.  
Reason: Correctness matters more than impressive plumbing.  
Trade-off: Future live ingestion would need additional background architecture.

## Shared market data by symbol
Context: Market facts are not user-specific.  
Decision: Store market observations and bars once per symbol/provider.  
Reason: User-specific state stays limited to watchlists, checkpoints, and receipts.  
Trade-off: Fixture resets affect all demo users.
