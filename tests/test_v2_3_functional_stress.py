"""Tests pour stress-tests fonctionnels v2.3."""

import pytest
import numpy as np
from isinglab.metrics.stress_test import (
    run_stress_test,
    stress_test_key_rules,
    create_test_patterns,
    apply_noise
)


def test_create_test_patterns():
    """Test création de patterns variés."""
    patterns = create_test_patterns((32, 32))
    
    # Devrait contenir plusieurs patterns
    assert len(patterns) >= 3
    
    # Tous devraient être des numpy arrays
    for p in patterns:
        assert isinstance(p, np.ndarray)
        assert p.shape == (32, 32)
        assert p.dtype == int


def test_apply_noise():
    """Test application de bruit."""
    grid = np.zeros((16, 16), dtype=int)
    grid[8, 8] = 1  # 1 cellule vivante
    
    # Noise = 0 → identique
    noisy_zero = apply_noise(grid, 0.0)
    assert np.array_equal(noisy_zero, grid)
    
    # Noise > 0 → différent
    noisy = apply_noise(grid, 0.2)
    assert not np.array_equal(noisy, grid)
    
    # Grille toujours binaire
    assert set(np.unique(noisy)).issubset({0, 1})


def test_run_stress_test_structure():
    """Test que stress_test retourne une structure valide."""
    # Règle triviale (tout meurt)
    def dead_rule(grid):
        return np.zeros_like(grid)
    
    result = run_stress_test(
        dead_rule,
        grid_sizes=[(16, 16), (32, 32)],
        noise_levels=[0.0, 0.1],
        steps=10,
        seed=42
    )
    
    # Vérifier structure
    assert 'config' in result
    assert 'by_grid_size' in result
    assert 'by_noise_level' in result
    assert 'summary' in result
    
    # Vérifier qu'on a bien 2 grilles testées
    assert len(result['by_grid_size']) == 2
    assert '16x16' in result['by_grid_size']
    assert '32x32' in result['by_grid_size']
    
    # Vérifier qu'on a bien 2 niveaux de bruit testés
    assert len(result['by_noise_level']) == 2
    
    # Vérifier summary
    assert 'avg_stability_across_sizes' in result['summary']
    assert 'avg_recall_across_noise' in result['summary']
    
    # Scores dans [0, 1]
    assert 0 <= result['summary']['avg_stability_across_sizes'] <= 1
    assert 0 <= result['summary']['avg_recall_across_noise'] <= 1


def test_stress_test_key_rules():
    """Test stress sur règles réelles."""
    rules = [
        {'notation': 'B3/S23', 'born': [3], 'survive': [2, 3]}
    ]
    
    result = stress_test_key_rules(
        rules,
        grid_sizes=[(16, 16)],  # 1 seule taille pour vitesse
        noise_levels=[0.0, 0.1],  # 2 niveaux
        output_file='results/test_stress.json'
    )
    
    assert 'B3/S23' in result
    assert 'summary' in result['B3/S23']
    
    # Cleanup
    import os
    if os.path.exists('results/test_stress.json'):
        os.remove('results/test_stress.json')


def test_server_module_import():
    """Test que le module server s'importe correctement."""
    try:
        from isinglab import server
        assert hasattr(server, 'run_server')
        assert hasattr(server, 'main')
    except ImportError as e:
        pytest.fail(f"Cannot import isinglab.server: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

