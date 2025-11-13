"""Pipelines de recherche et d'optimisation."""

from .regime_search import (
    run_regime_search,
    run_constrained_search,
    compare_systems_for_target
)
from .holonomy_optimization import (
    optimize_holonomy_path,
    simulate_with_holonomy_path,
    compare_trajectory_strategies
)
from .trajectory_cost import (
    TrajectoryMetrics,
    compute_trajectory_metrics,
    cost_efficiency,
    cost_stability,
    cost_violation,
    cost_control_effort
)

__all__ = [
    'run_regime_search',
    'run_constrained_search',
    'compare_systems_for_target',
    'optimize_holonomy_path',
    'simulate_with_holonomy_path',
    'compare_trajectory_strategies',
    'TrajectoryMetrics',
    'compute_trajectory_metrics',
    'cost_efficiency',
    'cost_stability',
    'cost_violation',
    'cost_control_effort'
]
