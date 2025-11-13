"""
Brain to Physical Systems Mapping v3.5

Heuristique: mapper profils dynamiques CA → systèmes physiques plausibles.

DISCLAIMER: Correspondances spéculatives basées sur métriques,
pas de validation expérimentale.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import json
from datetime import datetime


# Profils physiques hypothétiques
PHYSICAL_SYSTEMS = {
    'spin_glass': {
        'description': 'Spin glass / magnetic system',
        'desired_profile': {
            'robustness': 0.35,  # Moderate (thermal noise)
            'life_capacity': 0.50,  # Multiple stable states
            'density': 0.40,  # Balanced magnetization
            'basin_diversity': 0.60  # Multiple attractors
        }
    },
    'neural_network': {
        'description': 'Biological neural network',
        'desired_profile': {
            'robustness': 0.25,  # Sensitive to input
            'life_capacity': 0.65,  # Rich patterns
            'density': 0.15,  # Sparse activity
            'basin_diversity': 0.70  # Many attractors
        }
    },
    'robust_sensor': {
        'description': 'Robust environmental sensor',
        'desired_profile': {
            'robustness': 0.80,  # Very robust
            'life_capacity': 0.30,  # Simple states
            'density': 0.50,  # Moderate activity
            'basin_diversity': 0.30  # Few attractors
        }
    },
    'pattern_memory': {
        'description': 'Pattern memory / associative network',
        'desired_profile': {
            'robustness': 0.40,  # Moderate robustness
            'life_capacity': 0.70,  # High capacity
            'density': 0.20,  # Sparse encoding
            'basin_diversity': 0.75  # Many basins
        }
    },
    'phase_transition': {
        'description': 'Near phase transition / critical system',
        'desired_profile': {
            'robustness': 0.20,  # Sensitive
            'life_capacity': 0.60,  # Rich dynamics
            'density': 0.50,  # Balanced
            'basin_diversity': 0.50  # Moderate
        }
    }
}


def compute_profile_distance(ca_profile, phys_profile):
    """
    Euclidean distance between CA and physical system profiles.
    """
    dims = ['robustness', 'life_capacity', 'density', 'basin_diversity']
    
    distance = 0.0
    for dim in dims:
        ca_val = ca_profile.get(dim, 0.5)
        phys_val = phys_profile.get(dim, 0.5)
        distance += (ca_val - phys_val) ** 2
    
    return np.sqrt(distance)


def map_brain_to_physical(brain_modules_data):
    """
    Map each brain module to closest physical system.
    
    Returns mappings with distances.
    """
    mappings = []
    
    for module in brain_modules_data:
        if 'error' in module:
            continue
        
        notation = module['notation']
        metrics = module.get('metrics', {})
        
        # Extract CA profile
        ca_profile = {
            'robustness': metrics.get('robustness', {}).get('mean', 0.5),
            'life_capacity': metrics.get('life_capacity', {}).get('mean', 0.5),
            'density': metrics.get('density', {}).get('mean', 0.5),
            'basin_diversity': metrics.get('basin_diversity', {}).get('mean', 0.5)
        }
        
        # Compute distances to all physical systems
        distances = {}
        for phys_name, phys_info in PHYSICAL_SYSTEMS.items():
            distance = compute_profile_distance(ca_profile, phys_info['desired_profile'])
            distances[phys_name] = {
                'distance': float(distance),
                'description': phys_info['description']
            }
        
        # Sort by distance
        sorted_matches = sorted(distances.items(), key=lambda x: x[1]['distance'])
        
        mapping = {
            'notation': notation,
            'ca_profile': {k: float(v) for k, v in ca_profile.items()},
            'closest_match': sorted_matches[0][0],
            'closest_match_distance': sorted_matches[0][1]['distance'],
            'closest_match_description': sorted_matches[0][1]['description'],
            'all_matches': {k: v for k, v in sorted_matches[:3]}  # Top 3
        }
        
        mappings.append(mapping)
    
    return mappings


def generate_hypotheses(mappings):
    """Generate plausible hypotheses from mappings."""
    hypotheses = []
    
    # Group by physical system
    phys_groups = {}
    for mapping in mappings:
        phys = mapping['closest_match']
        if phys not in phys_groups:
            phys_groups[phys] = []
        phys_groups[phys].append(mapping['notation'])
    
    # Generate hypotheses
    for phys, ca_rules in phys_groups.items():
        phys_desc = PHYSICAL_SYSTEMS[phys]['description']
        
        hypothesis = {
            'physical_system': phys,
            'description': phys_desc,
            'candidate_ca_rules': ca_rules,
            'hypothesis': f"CA rules {', '.join(ca_rules)} exhibit dynamic profiles similar to {phys_desc}",
            'status': 'SPECULATIVE - requires experimental validation',
            'suggested_tests': [
                "Compare attractor landscapes",
                "Test response to perturbations",
                "Measure information capacity"
            ]
        }
        
        hypotheses.append(hypothesis)
    
    return hypotheses


def main():
    print("="*80)
    print("BRAIN TO PHYSICAL SYSTEMS MAPPING v3.5")
    print("="*80)
    print()
    print("DISCLAIMER: Heuristic mappings based on metrics.")
    print("NOT experimental validation. Speculative correspondences only.")
    print()
    
    # Load brain modules data
    brain_data_path = Path("results/brain_modules_v3_5.json")
    
    if not brain_data_path.exists():
        print(f"ERROR: {brain_data_path} not found.")
        print("Run scripts/consolidate_brain_modules_v3_5.py first.")
        return
    
    with open(brain_data_path) as f:
        brain_data = json.load(f)
    
    modules = brain_data.get('modules', [])
    
    # Compute mappings
    print("Computing profile distances...")
    mappings = map_brain_to_physical(modules)
    
    # Generate hypotheses
    print("Generating hypotheses...")
    hypotheses = generate_hypotheses(mappings)
    
    # Display
    print("\n" + "="*80)
    print("MAPPINGS")
    print("="*80)
    
    for mapping in mappings:
        print(f"\n{mapping['notation']}:")
        print(f"  Closest match: {mapping['closest_match']} ({mapping['closest_match_description']})")
        print(f"  Distance: {mapping['closest_match_distance']:.3f}")
        print(f"  CA profile: rob={mapping['ca_profile']['robustness']:.2f}, "
              f"cap={mapping['ca_profile']['life_capacity']:.2f}, "
              f"dens={mapping['ca_profile']['density']:.2f}, "
              f"div={mapping['ca_profile']['basin_diversity']:.2f}")
    
    print("\n" + "="*80)
    print("HYPOTHESES (SPECULATIVE)")
    print("="*80)
    
    for i, hyp in enumerate(hypotheses, 1):
        print(f"\n{i}. {hyp['physical_system']} ({hyp['description']})")
        print(f"   Candidate CA rules: {', '.join(hyp['candidate_ca_rules'])}")
        print(f"   Hypothesis: {hyp['hypothesis']}")
        print(f"   Status: {hyp['status']}")
    
    # Save
    output_dir = Path("results")
    output_data = {
        'meta': {
            'version': '3.5',
            'date': datetime.now().isoformat(),
            'disclaimer': 'Speculative mappings based on metrics. Not experimental validation.'
        },
        'physical_systems': PHYSICAL_SYSTEMS,
        'mappings': mappings,
        'hypotheses': hypotheses
    }
    
    with open(output_dir / "brain_physical_mapping_v3_5.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved: results/brain_physical_mapping_v3_5.json")


if __name__ == "__main__":
    main()

