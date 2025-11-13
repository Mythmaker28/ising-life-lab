"""Contrôle holonomique : strokes, trajectoires, phase de Berry, optimisation."""

from .holonomy import (
    HolonomyPath,
    StrokeLibrary,
    generate_linear_ramp_path,
    generate_smooth_sigmoid_path,
    generate_multi_stage_path,
    generate_closed_loop_path,
    generate_adaptive_loop_path
)
from .optimizers import (
    GridSearchOptimizer,
    RandomSearchOptimizer,
    OptimizationResult
)

__all__ = [
    'HolonomyPath',
    'StrokeLibrary',
    'generate_linear_ramp_path',
    'generate_smooth_sigmoid_path',
    'generate_multi_stage_path',
    'generate_closed_loop_path',
    'generate_adaptive_loop_path',
    'GridSearchOptimizer',
    'RandomSearchOptimizer',
    'OptimizationResult'
]

