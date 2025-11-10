"""
Ising Life Lab - Experimental framework for CA and Ising systems.

This package provides tools for exploring cellular automata, Ising-like systems,
and their edge-of-chaos behaviors.
"""

__version__ = "0.1.0"
__author__ = "Mythmaker28"

from .api import evaluate_rule, evaluate_batch

__all__ = ["evaluate_rule", "evaluate_batch"]

