"""Pipelines de recherche et d'optimisation."""

from .regime_search import (
    run_regime_search,
    run_constrained_search,
    compare_systems_for_target
)
from .holonomy_optimization import (
    optimize_holonomy_path,
    simulate_with_holonomy_path,
    compare_trajectory_strategies,
    compare_geometric_vs_dynamic_robustness
)
from .trajectory_cost import (
    TrajectoryMetrics,
    compute_trajectory_metrics,
    cost_efficiency,
    cost_stability,
    cost_violation,
    cost_control_effort,
    cost_geometric_phase,
    cost_robustness_to_noise
)
from .batch_processing import (
    run_atlas_batch_processing,
    generate_strategy_recommendations
)

__all__ = [
    'run_regime_search',
    'run_constrained_search',
    'compare_systems_for_target',
    'optimize_holonomy_path',
    'simulate_with_holonomy_path',
    'compare_trajectory_strategies',
    'compare_geometric_vs_dynamic_robustness',
    'TrajectoryMetrics',
    'compute_trajectory_metrics',
    'cost_efficiency',
    'cost_stability',
    'cost_violation',
    'cost_control_effort',
    'cost_geometric_phase',
    'cost_robustness_to_noise',
    'run_atlas_batch_processing',
    'generate_strategy_recommendations'
]
