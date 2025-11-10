"""
Example: End-to-End Atlas → Regime Search Pipeline

This script demonstrates how to:
1. Load systems from Biological Qubits Atlas
2. Map their properties to conceptual categories
3. Generate target CA/Ising profiles
4. Search for matching rules/regimes
5. Export results for further AI analysis

REQUIREMENTS:
- Atlas CSV files in data/ directory (see data/README.md)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.data_bridge import (
    load_optical_systems,
    load_spin_qubits,
    load_nuclear_spins,
    load_radical_pairs,
    map_system_properties,
    generate_system_profiles
)
from isinglab.mapping_profiles import get_target_profile_for_system
from isinglab.pipelines import run_regime_search


def main():
    print("=" * 80)
    print("ISING LIFE LAB × BIOLOGICAL QUBITS ATLAS")
    print("End-to-End Example: Physical Systems → CA/Ising Regimes")
    print("=" * 80)
    print()
    
    # ========================================================================
    # STEP 1: Load Systems from Atlas (READ-ONLY)
    # ========================================================================
    
    print("📊 STEP 1: Loading systems from Atlas...")
    print()
    
    systems = {}
    
    try:
        optical = load_optical_systems(tier="curated")
        print(f"  ✓ Optical systems: {len(optical)} loaded (Tier 1 curated)")
        systems['optical'] = optical
    except Exception as e:
        print(f"  ⚠ Optical systems: Not available ({e})")
    
    try:
        spins = load_spin_qubits()
        print(f"  ✓ Spin qubits: {len(spins)} loaded")
        systems['spin'] = spins
    except Exception as e:
        print(f"  ⚠ Spin qubits: Not available ({e})")
    
    try:
        nuclear = load_nuclear_spins()
        print(f"  ✓ Nuclear spins: {len(nuclear)} loaded")
        systems['nuclear'] = nuclear
    except Exception as e:
        print(f"  ⚠ Nuclear spins: Not available ({e})")
    
    try:
        radical = load_radical_pairs()
        print(f"  ✓ Radical pairs: {len(radical)} loaded")
        systems['radical_pair'] = radical
    except Exception as e:
        print(f"  ⚠ Radical pairs: Not available ({e})")
    
    if not systems:
        print()
        print("❌ No Atlas CSV files found. See data/README.md for setup instructions.")
        print()
        print("Quick setup:")
        print("  1. Clone Atlas repo: git clone https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology.git")
        print("  2. Copy CSV files to data/ directory")
        print("  3. Re-run this script")
        return
    
    print()
    print(f"Total systems loaded: {sum(len(df) for df in systems.values())}")
    print()
    
    # ========================================================================
    # STEP 2: Map System Properties (Heuristic, Deterministic)
    # ========================================================================
    
    print("🗺️  STEP 2: Mapping system properties...")
    print()
    
    mapped_systems = {}
    for modality, df in systems.items():
        df_mapped = map_system_properties(df)
        mapped_systems[modality] = df_mapped
        
        print(f"  {modality.upper()}:")
        
        # Count by coherence class
        if 'coherence_class' in df_mapped.columns:
            coherence_counts = df_mapped['coherence_class'].value_counts()
            for cclass, count in coherence_counts.items():
                print(f"    - {cclass}: {count}")
        else:
            print(f"    - Total: {len(df_mapped)}")
    
    print()
    
    # ========================================================================
    # STEP 3: Generate Target Profiles for Representative Systems
    # ========================================================================
    
    print("🎯 STEP 3: Generating target CA/Ising profiles...")
    print()
    
    # Example: Long-coherence optical system (e.g., GCaMP8s)
    profile_optical_long = get_target_profile_for_system(
        modality="optical",
        temperature_regime="physiological",
        coherence_class="long"
    )
    
    print("  Profile 1: Optical + Physiological + Long Coherence")
    print(f"    Target edge_score: {profile_optical_long['target_metrics']['edge_score']}")
    print(f"    Target memory_score: {profile_optical_long['target_metrics']['memory_score']}")
    print(f"    Rationale: {profile_optical_long['rationale'][:60]}...")
    print()
    
    # Example: NV center (spin, room temp, long coherence)
    profile_spin_long = get_target_profile_for_system(
        modality="spin",
        temperature_regime="physiological",
        coherence_class="long"
    )
    
    print("  Profile 2: Spin + Physiological + Long Coherence (e.g., NV center)")
    print(f"    Target edge_score: {profile_spin_long['target_metrics']['edge_score']}")
    print(f"    Target memory_score: {profile_spin_long['target_metrics']['memory_score']}")
    print()
    
    # ========================================================================
    # STEP 4: Run Regime Search for Each Profile
    # ========================================================================
    
    print("🔍 STEP 4: Searching CA/Ising regimes...")
    print()
    
    # Search for optical long-coherence profile (quick scan)
    print("  Searching for Profile 1 (optical long-coherence)...")
    results_optical, top_optical = run_regime_search(
        target_profile=profile_optical_long,
        rule_pool=list(range(0, 100)),  # Quick scan: rules 0-99
        ca_type="elementary",
        grid_size=50,
        steps=100,
        seeds_per_rule=2,
        base_seed=42,
        output_dir="outputs/atlas_demo_optical_long"
    )
    
    print(f"    ✓ Evaluated {len(results_optical)} rules")
    print(f"    ✓ Top rule: {top_optical[0]['rule']} (edge_score={top_optical[0]['edge_score']:.3f}, memory={top_optical[0]['memory_score']:.3f})")
    print()
    
    # ========================================================================
    # STEP 5: Summary & Interpretation
    # ========================================================================
    
    print("=" * 80)
    print("📝 SUMMARY")
    print("=" * 80)
    print()
    print("Systems analyzed:")
    for modality, df in mapped_systems.items():
        print(f"  - {modality.upper()}: {len(df)} systems")
    print()
    print("Top CA rules for long-coherence optical systems:")
    for i, rule_data in enumerate(top_optical[:5]):
        print(f"  {i+1}. Rule {rule_data['rule']:3d} : edge={rule_data['edge_score']:.3f}, memory={rule_data['memory_score']:.3f}")
    print()
    print("Outputs saved to:")
    print("  - outputs/atlas_demo_optical_long/regime_search_results.csv")
    print("  - outputs/atlas_demo_optical_long/top_rules.json")
    print()
    print("⚠️  INTERPRETATION:")
    print("  Ces règles CA partagent des caractéristiques QUALITATIVES avec")
    print("  les systèmes optiques à longue cohérence (stabilité + sensibilité modérée).")
    print("  Cela NE prédit PAS le comportement quantique réel ni T₂.")
    print()
    print("  Utilité: Explorer l'espace des régimes dynamiques pour identifier")
    print("  des patterns génériques (edge-of-chaos, mémoire, etc.) qui POURRAIENT")
    print("  être pertinents pour le design de systèmes biologiques computationnels.")
    print()


if __name__ == "__main__":
    main()

