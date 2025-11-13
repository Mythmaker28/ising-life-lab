"""Ising Life Lab - experimental framework."""

__version__ = "0.1.0"
__author__ = "Mythmaker28"

from .api import evaluate_rule, evaluate_batch
from .closed_loop_agi import ClosedLoopAGI
from .meta_learner import (
    MemoryAggregator,
    train_meta_model,
    CandidateSelector,
)
from .brain_modules import (
    BRAIN_MODULES,
    get_brain,
    list_brains,
    get_brain_by_notation,
    get_brain_rule_function,
    get_tier1_brains,
)
from . import reservoir
from . import oscillators
from . import analysis
from . import control

__all__ = [
    'evaluate_rule',
    'evaluate_batch',
    'ClosedLoopAGI',
    'MemoryAggregator',
    'train_meta_model',
    'CandidateSelector',
    'BRAIN_MODULES',
    'get_brain',
    'list_brains',
    'get_brain_by_notation',
    'get_brain_rule_function',
    'get_tier1_brains',
    'reservoir',
    'oscillators',
    'analysis',
    'control',
]
