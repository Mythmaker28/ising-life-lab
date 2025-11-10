"""
Data bridge for reading Atlas data (READ-ONLY)
"""
from .atlas_loader import (
    load_optical_systems,
    load_nonoptical_systems,
    load_spin_qubits,
    load_nuclear_spins,
    load_radical_pairs,
    list_available_datasets
)
from .mapping import map_system_properties, generate_system_profiles

__all__ = [
    "load_optical_systems",
    "load_nonoptical_systems",
    "load_spin_qubits",
    "load_nuclear_spins",
    "load_radical_pairs",
    "list_available_datasets",
    "map_system_properties",
    "generate_system_profiles"
]

