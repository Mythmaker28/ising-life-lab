"""
Test Tâches Morphologiques v5.0 — Opérations morphologiques via CA.

Teste si CA peuvent servir d'opérateurs morphologiques "gratuits".
"""

import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy.ndimage import binary_erosion, binary_dilation, label

from isinglab.brain_modules import get_brain_rule_function


def generate_binary_shapes(n_samples=100, grid_size=(64, 64), seed=42):
    """Génère formes binaires pour tests morphologiques."""
    np.random.seed(seed)
    h, w = grid_size
    shapes = []
    
    for _ in range(n_samples):
        shape = np.zeros((h, w))
        # 2-4 objets aléatoires
        n_objects = np.random.randint(2, 5)
        for _ in range(n_objects):
            cx, cy = np.random.randint(10, h-10), np.random.randint(10, w-10)
            radius = np.random.randint(5, 15)
            for i in range(max(0, cx-radius), min(h, cx+radius)):
                for j in range(max(0, cy-radius), min(w, cy+radius)):
                    if (i - cx)**2 + (j - cy)**2 < radius**2:
                        shape[i, j] = 1
        shapes.append(shape)
    
    return np.array(shapes)


def test_connected_components(brain_name, shapes, steps=5):
    """
    Teste si CA préserve composantes connexes.
    
    Idée : Si CA est "morphologique", il devrait préserver nombre de composantes.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    preservation_scores = []
    
    for shape in shapes:
        # Composantes initiales
        labeled_init, n_init = label(shape)
        
        # Évolution CA
        evolved = shape.copy()
        for _ in range(steps):
            evolved = rule_func(evolved)
        
        # Composantes finales
        labeled_final, n_final = label(evolved)
        
        # Score : préservation du nombre de composantes
        if n_init > 0:
            score = min(n_final, n_init) / max(n_final, n_init, 1)
        else:
            score = 1.0 if n_final == 0 else 0.0
        
        preservation_scores.append(score)
    
    avg_score = np.mean(preservation_scores)
    
    return {
        'preservation_score': avg_score,
        'method': f'CA_{brain_name}'
    }


def test_erosion_quality(brain_name, shapes, steps=3):
    """
    Teste si CA fait érosion (réduction objets).
    
    Compare avec érosion morphologique classique.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Érosion classique
    shapes_eroded_classic = np.array([binary_erosion(s, iterations=steps) for s in shapes])
    
    # "Érosion" via CA
    shapes_eroded_ca = []
    for shape in shapes:
        evolved = shape.copy()
        for _ in range(steps):
            evolved = rule_func(evolved)
        shapes_eroded_ca.append(evolved)
    shapes_eroded_ca = np.array(shapes_eroded_ca)
    
    # Métrique : similarité avec érosion classique
    # (Si CA fait érosion, devrait être similaire)
    similarity = []
    for s_classic, s_ca in zip(shapes_eroded_classic, shapes_eroded_ca):
        # IoU-like
        intersection = np.sum((s_classic == 1) & (s_ca == 1))
        union = np.sum((s_classic == 1) | (s_ca == 1))
        iou = intersection / union if union > 0 else 0.0
        similarity.append(iou)
    
    avg_similarity = np.mean(similarity)
    
    # Densité CA vs classique
    density_ca = np.mean([s.mean() for s in shapes_eroded_ca])
    density_classic = np.mean([s.mean() for s in shapes_eroded_classic])
    
    return {
        'erosion_similarity': avg_similarity,
        'density_ca': density_ca,
        'density_classic': density_classic,
        'method': f'CA_{brain_name}'
    }


def test_dilation_quality(brain_name, shapes, steps=3):
    """
    Teste si CA fait dilatation (expansion objets).
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Dilatation classique
    shapes_dilated_classic = np.array([binary_dilation(s, iterations=steps) for s in shapes])
    
    # "Dilatation" via CA
    shapes_dilated_ca = []
    for shape in shapes:
        evolved = shape.copy()
        for _ in range(steps):
            evolved = rule_func(evolved)
        shapes_dilated_ca.append(evolved)
    shapes_dilated_ca = np.array(shapes_dilated_ca)
    
    # Similarité
    similarity = []
    for s_classic, s_ca in zip(shapes_dilated_classic, shapes_dilated_ca):
        intersection = np.sum((s_classic == 1) & (s_ca == 1))
        union = np.sum((s_classic == 1) | (s_ca == 1))
        iou = intersection / union if union > 0 else 0.0
        similarity.append(iou)
    
    avg_similarity = np.mean(similarity)
    
    # Densité
    density_ca = np.mean([s.mean() for s in shapes_dilated_ca])
    density_classic = np.mean([s.mean() for s in shapes_dilated_classic])
    
    return {
        'dilation_similarity': avg_similarity,
        'density_ca': density_ca,
        'density_classic': density_classic,
        'method': f'CA_{brain_name}'
    }


def test_edge_detection(brain_name, shapes, steps=1):
    """
    Teste si CA détecte bords (différence avant/après 1 step).
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Bords classiques (sobel-like)
    from scipy.ndimage import sobel
    edges_classic = []
    for shape in shapes:
        sx = sobel(shape.astype(float), axis=0)
        sy = sobel(shape.astype(float), axis=1)
        edges = np.sqrt(sx**2 + sy**2)
        edges_binary = (edges > 0.1).astype(int)
        edges_classic.append(edges_binary)
    edges_classic = np.array(edges_classic)
    
    # "Bords" via CA : différence input/output
    edges_ca = []
    for shape in shapes:
        evolved = rule_func(shape)
        # Différence = potentiellement bords
        diff = np.abs(shape - evolved)
        edges_ca.append(diff)
    edges_ca = np.array(edges_ca)
    
    # Similarité
    similarity = []
    for e_classic, e_ca in zip(edges_classic, edges_ca):
        intersection = np.sum((e_classic == 1) & (e_ca == 1))
        union = np.sum((e_classic == 1) | (e_ca == 1))
        iou = intersection / union if union > 0 else 0.0
        similarity.append(iou)
    
    avg_similarity = np.mean(similarity)
    
    return {
        'edge_similarity': avg_similarity,
        'method': f'CA_{brain_name}'
    }


def main():
    """
    Lance tests morphologiques pour brain modules.
    """
    print("=" * 80)
    print("TEST TÂCHES MORPHOLOGIQUES v5.0")
    print("=" * 80)
    
    # Configuration
    grid_size = (64, 64)
    n_samples = 100
    seed = 42
    
    # Générer données
    print("\n[GENERATING DATA]")
    print("  Binary shapes...", end=' ', flush=True)
    shapes = generate_binary_shapes(n_samples, grid_size, seed)
    print(f"OK ({len(shapes)} samples)")
    
    # Brain modules
    brain_names = ['life', 'highlife', 'life_dense', '34life']
    
    # Résultats
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'config': {'grid_size': grid_size, 'n_samples': n_samples, 'seed': seed},
        'connected_components': [],
        'erosion': [],
        'dilation': [],
        'edge_detection': []
    }
    
    # Test 1 : Composantes connexes
    print("\n[TEST 1: PRESERVATION COMPOSANTES CONNEXES]")
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_connected_components(brain_name, shapes, steps=5)
        result['elapsed'] = time.time() - start
        all_results['connected_components'].append(result)
        print(f"preservation={result['preservation_score']:.3f} (t={result['elapsed']:.2f}s)")
    
    # Test 2 : Érosion
    print("\n[TEST 2: EROSION-LIKE BEHAVIOR]")
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_erosion_quality(brain_name, shapes, steps=3)
        result['elapsed'] = time.time() - start
        all_results['erosion'].append(result)
        print(f"similarity={result['erosion_similarity']:.3f} "
              f"(dens CA={result['density_ca']:.3f} vs classic={result['density_classic']:.3f})")
    
    # Test 3 : Dilatation
    print("\n[TEST 3: DILATION-LIKE BEHAVIOR]")
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_dilation_quality(brain_name, shapes, steps=3)
        result['elapsed'] = time.time() - start
        all_results['dilation'].append(result)
        print(f"similarity={result['dilation_similarity']:.3f} "
              f"(dens CA={result['density_ca']:.3f} vs classic={result['density_classic']:.3f})")
    
    # Test 4 : Détection bords
    print("\n[TEST 4: EDGE DETECTION]")
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_edge_detection(brain_name, shapes, steps=1)
        result['elapsed'] = time.time() - start
        all_results['edge_detection'].append(result)
        print(f"similarity={result['edge_similarity']:.3f} (t={result['elapsed']:.2f}s)")
    
    # Sauvegarder
    output_dir = Path('results/brain_niches_v5')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'morpho_tasks.json'
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("TEST MORPHOLOGIQUE COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    
    # Analyse
    print("\n[ANALYSE]")
    print("\nPreservation composantes:")
    for r in sorted(all_results['connected_components'], key=lambda x: x['preservation_score'], reverse=True):
        print(f"  {r['method']:20s}: {r['preservation_score']:.3f}")
    
    print("\nSimilarite erosion:")
    for r in sorted(all_results['erosion'], key=lambda x: x['erosion_similarity'], reverse=True):
        print(f"  {r['method']:20s}: {r['erosion_similarity']:.3f}")


if __name__ == '__main__':
    main()


