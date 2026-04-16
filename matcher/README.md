# matcher

Stable assignment and quota management for toxicity-aware corridor allocation.

## Responsibilities

- Allocate commuters to equilibrium corridors using stable matching.
- Manage capacity constraints and user preferences.
- Support nearest-distance fallback for unmatched users.
- Enforce segment-level preferences and quota limits.

## Main Files

- `gale_shapley.py`: Stable matching algorithm with capacity and preference support.
- `quota_manager.py`: Quota tracking and enforcement across corridors.
- `commuter_model.py`: Commuter preference modeling and ranking.
- `segment_model.py`: Segment (corridor section) capacity and feature models.
- `equilibrium_checker.py`: Validation and stability verification of assignments.
- `route_pool.py`: Route pool management and filtering.

## Matching Algorithm

The matcher implements the **Gale-Shapley stable matching algorithm** with extensions:

1. **Capacity Support**
   - Each corridor has a maximum capacity constraint.
   - Prevents demand collapse into a single route.

2. **User Preferences**
   - Commuters rank corridors based on toxicity exposure, distance, and time.
   - Preferences derived from GNN-computed edge weights and historical data.

3. **Segment-Level Control**
   - Enforce preferences on specific route segments (e.g., "avoid this intersection").
   - Support isolation-focused behavior during pollution spikes.

4. **Nearest-Distance Fallback**
   - Unmatched users assigned to nearest available route.
   - Ensures complete allocation under capacity constraints.

## Workflow

1. **Compute User Preferences**
   - Rank available corridors based on current toxicity state and user constraints.
   - Use stream-backed edge weights from GNN layer.

2. **Enforce Quotas**
   - Set per-corridor capacity limits (e.g., max 50 users per route).
   - Track active assignments.

3. **Run Stable Matching**
   - Gale-Shapley algorithm returns stable assignment or partial assignment with fallback.

4. **Validate Equilibrium**
   - Verify no pair (user, corridor) can improve by swapping.
   - Check capacity constraints are met.

## Mode Policy

- Matcher mode profiles are tuned for `jogger`, `cyclist`, and `two_wheeler`.
- Legacy `car` inputs are still accepted and mapped to the same weighting profile as `two_wheeler` for backward compatibility.

## Integration with Routing

The matcher accepts toxicity-aware routes from the router's A* search and allocates commuters across them:

```python
from matcher.gale_shapley import stable_match
from matcher.quota_manager import QuotaManager

# Receive routes from router, compute user preferences
routes = router.compute_routes(start, end, toxicity_weights)
prefs = commuter_model.get_preference_ranking(user, routes)

# Allocate users to corridors
quotas = QuotaManager(capacity_per_route=50)
assignment = stable_match(users, routes, prefs, quotas)
```

## Configuration

Matcher settings are in `shared/config.py`:

- Grid bounding box for geometry.
- Capacity defaults per corridor.
- Preference weighting (toxicity vs. distance vs. ETA).

## Testing

Unit tests are in `tests/`:

```bash
pytest matcher/tests/
```

Key test coverage:

- Stable matching correctness under preferences.
- Capacity constraint enforcement.
- Equilibrium validation.
- Nearest-distance fallback behavior.
- Segment-level preference application.
