"""Analyse de champs : défauts topologiques, projections, statistiques."""

from .defects import detect_vortices, compute_winding_number, DefectMetrics
from .projection import ProjectionMap

__all__ = ['detect_vortices', 'compute_winding_number', 'DefectMetrics', 'ProjectionMap']

