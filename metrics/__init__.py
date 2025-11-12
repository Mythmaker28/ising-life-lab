"""
Metrics module for ising-life-lab toolkit

Provides scoring functions for design space analysis.
"""

from .functional_score import (
    compute_functional_score,
    apply_functional_score,
    get_score_weights
)

__all__ = [
    'compute_functional_score',
    'apply_functional_score',
    'get_score_weights'
]

__version__ = '1.0.0'

