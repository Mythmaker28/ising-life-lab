"""
ISING-ATLAS BRIDGE DEMO

Démontre le mapping conceptuel entre modules mémoire Ising et systèmes physiques
catalogués dans l'Atlas Quantum-Sensors-Qubits-in-Biology.

IMPORTANT : Bridge conceptuel heuristique, pas validation expérimentale.
"""

from isinglab.integration import PHYSICAL_TARGET_PROFILES
from isinglab.integration.module_matcher import (
    rank_modules_for_profile,
    suggest_modules_for_system_features
)


def main():
    print("=" * 80)
    print("ISING-ATLAS BRIDGE DEMO v2.1")
    print("=" * 80)
    
    # Vérifier que l'export existe
    import os
    if not os.path.exists('results/agi_export_hof.json'):
        print("[ERROR] Export AGI introuvable. Exécutez: python -m isinglab.export_memory_library")
        return 1
    
    print("\n[OK] Export AGI chargé : results/agi_export_hof.json\n")
    
    # === Scénario 1 : Système NV-like ===
    print("=" * 80)
    print("SCENARIO 1: NV-like Diamond System (solid-state, high coherence)")
    print("=" * 80)
    
    nv_features = {
        'system_class': 'NV diamond',
        'modality': 'optical + RF',
        'temp_k': 300,
        'noise_environment': 'low',
        'integration_hint': 'cavity-coupled'
    }
    
    suggestions = suggest_modules_for_system_features(nv_features, top_k=3)
    
    if suggestions:
        print(f"\nTop 3 modules Ising recommandés (profil: {suggestions[0][2]}):")
        for i, (score, module, profile) in enumerate(suggestions, 1):
            notation = module['notation']
            scores = module['scores']
            labels = module.get('labels', [])[:3]
            print(f"  {i}. {notation} (score={score:.3f})")
            print(f"     Composite: {scores.get('composite', 0):.3f}, Labels: {labels}")
    else:
        print("\n[WARN] Aucun module trouvé")
    
    # === Scénario 2 : Biosenseur optique ===
    print("\n" + "=" * 80)
    print("SCENARIO 2: Biosensor (GCaMP-like, in vivo, noisy)")
    print("=" * 80)
    
    biosensor_features = {
        'system_class': 'GCaMP calcium sensor',
        'modality': 'optical fluorescence',
        'temp_k': 310,
        'noise_environment': 'high',
        'integration_hint': 'in vivo'
    }
    
    suggestions = suggest_modules_for_system_features(biosensor_features, top_k=3)
    
    if suggestions:
        print(f"\nTop 3 modules Ising recommandés (profil: {suggestions[0][2]}):")
        for i, (score, module, profile) in enumerate(suggestions, 1):
            notation = module['notation']
            scores = module['scores']
            labels = module.get('labels', [])[:3]
            print(f"  {i}. {notation} (score={score:.3f})")
            print(f"     Composite: {scores.get('composite', 0):.3f}, Labels: {labels}")
    else:
        print("\n[WARN] Aucun module trouvé")
    
    # === Scénario 3 : Radical pair bio-spin ===
    print("\n" + "=" * 80)
    print("SCENARIO 3: Radical Pair (cryptochrome-like, magnetic sensing)")
    print("=" * 80)
    
    radical_features = {
        'system_class': 'radical pair cryptochrome',
        'modality': 'magnetic',
        'temp_k': 298,
        'noise_environment': 'high',
        'integration_hint': 'biological'
    }
    
    suggestions = suggest_modules_for_system_features(radical_features, top_k=3)
    
    if suggestions:
        print(f"\nTop 3 modules Ising recommandés (profil: {suggestions[0][2]}):")
        for i, (score, module, profile) in enumerate(suggestions, 1):
            notation = module['notation']
            scores = module['scores']
            labels = module.get('labels', [])[:3]
            print(f"  {i}. {notation} (score={score:.3f})")
            print(f"     Composite: {scores.get('composite', 0):.3f}, Labels: {labels}")
    else:
        print("\n[WARN] Aucun module trouvé")
    
    # === Profils disponibles ===
    print("\n" + "=" * 80)
    print("PROFILS PHYSIQUES DISPONIBLES")
    print("=" * 80)
    
    for name, profile in PHYSICAL_TARGET_PROFILES.items():
        print(f"\n{name}:")
        print(f"  Description: {profile.description}")
        print(f"  Profils Ising préférés: {profile.preferred_module_profiles}")
        print(f"  Classes Atlas (conceptuel): {profile.atlas_system_classes[:2] if profile.atlas_system_classes else []}")
    
    print("\n" + "=" * 80)
    print("[OK] Demo terminee. Bridge conceptuel Ising <-> Atlas operationnel.")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    exit(main())

