"""
Design Space module v1.0

Outils pour interroger et analyser la cartographie des systèmes biologiques
quantiques/senseurs.
"""

from .selector import (
    load_design_space,
    list_room_temp_candidates,
    list_bio_adjacent_candidates,
    list_high_contrast_candidates,
    list_near_infrared_candidates,
    rank_by_integrability,
    filter_by_family,
    get_system_by_id,
    get_families,
    get_stats_summary
)

from .loaders import (
    load_atlas_optical,
    load_generic_design_space,
    validate_design_space_schema,
    convert_atlas_to_design_space,
    list_available_atlas_tiers,
    get_column_summary
)

from .pareto import (
    compute_pareto_front,
    rank_pareto,
    get_pareto_summary
)

__all__ = [
    # Selector functions
    'load_design_space',
    'list_room_temp_candidates',
    'list_bio_adjacent_candidates',
    'list_high_contrast_candidates',
    'list_near_infrared_candidates',
    'rank_by_integrability',
    'filter_by_family',
    'get_system_by_id',
    'get_families',
    'get_stats_summary',
    # Loader functions
    'load_atlas_optical',
    'load_generic_design_space',
    'validate_design_space_schema',
    'convert_atlas_to_design_space',
    'list_available_atlas_tiers',
    'get_column_summary',
    # Pareto functions
    'compute_pareto_front',
    'rank_pareto',
    'get_pareto_summary'
]

__version__ = '1.0.0'

