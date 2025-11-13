"""
Reservoir __init__.py
"""

from .core import CAReservoir
from .eval import (
    generate_narma10,
    generate_narma20,
    generate_mackey_glass,
    generate_denoising_data,
    evaluate_narma,
    evaluate_mackey_glass,
    evaluate_denoising
)
from .baselines import SimpleESN, SimpleMLP, LinearBaseline

__all__ = [
    'CAReservoir',
    'generate_narma10',
    'generate_narma20',
    'generate_mackey_glass',
    'generate_denoising_data',
    'evaluate_narma',
    'evaluate_mackey_glass',
    'evaluate_denoising',
    'SimpleESN',
    'SimpleMLP',
    'LinearBaseline'
]



