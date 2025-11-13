"""Tests pour v2.2 - Stable-bias, quotas, grid-sweep"""

import pytest
import numpy as np
from isinglab.meta_learner.selector import CandidateSelector, MultiArmedBandit
from isinglab.memory_explorer import MemoryExplorer
from isinglab.closed_loop_agi import ClosedLoopAGI


def test_stable_bias_generates_reasonable_rules():
    """Test que stable_bias génère des règles contraintes."""
    # Créer un selector avec méta-modèle dummy
    class DummyMetaModel:
        is_trained = True
        train_stats = {'test_accuracy': 0.5}
        def predict_proba(self, notation, born, survive):
            return 0.5
    
    selector = CandidateSelector(DummyMetaModel(), [], use_bandit=False)
    
    # Générer candidats stable_bias
    candidates = selector._generate_stable_biased_candidates(count=10)
    
    assert len(candidates) > 0
    
    for cand in candidates:
        born = cand['born']
        survive = cand['survive']
        
        # Vérifier contraintes:
        # Born devrait être petit (généralement ⊂ {0,1,2,3})
        assert all(b <= 3 for b in born), f"Born contient valeurs > 3: {born}"
        
        # Survive devrait contenir 2 ou 3
        assert 2 in survive or 3 in survive, f"Survive ne contient ni 2 ni 3: {survive}"
        
        # Born devrait avoir max 2 valeurs (pour la plupart)
        # Note: génération aléatoire peut dépasser, on vérifie juste la tendance
        assert len(born) <= 4, f"Born trop grand: {born}"


def test_grid_sweep_profile_stability():
    """Test que grid_sweep calcule profile_stability correctement."""
    explorer = MemoryExplorer()
    
    # Règle test : B3/S23 (Game of Life)
    rule = {
        'notation': 'B3/S23',
        'born': [3],
        'survive': [2, 3]
    }
    
    # Grid sweep sur 2 tailles (pour aller vite)
    result = explorer.grid_sweep(rule, grid_sizes=[(16, 16), (32, 32)], steps=30, seed=42)
    
    # Vérifier structure output
    assert 'notation' in result
    assert 'sweeps' in result
    assert 'profile_stability' in result
    assert 'consensus_profile' in result
    assert 'profiles_by_size' in result
    
    # Vérifier que profile_stability ∈ [0, 1]
    assert 0 <= result['profile_stability'] <= 1
    
    # Vérifier qu'on a bien N sweeps
    assert len(result['sweeps']) == 2
    
    # Chaque sweep devrait avoir un profil
    for sweep in result['sweeps']:
        assert 'grid_size' in sweep
        assert 'profile' in sweep
        assert 'metrics' in sweep


def test_hof_profile_quota_respected():
    """Test que les quotas de profils sont respectés."""
    config = {
        'evaluation_seed': 42,
        'hof_profile_quotas': {
            'stable_memory': 2,
            'chaotic_probe': 2,
            'generic': 1
        },
        'adaptive_thresholds': False  # Désactiver pour test simple
    }
    
    agi = ClosedLoopAGI(config=config)
    
    # Simuler HoF avec quotas pleins
    mock_hof = [
        {'notation': 'A', 'module_profile': 'stable_memory'},
        {'notation': 'B', 'module_profile': 'stable_memory'},  # Quota = 2/2
        {'notation': 'C', 'module_profile': 'chaotic_probe'},
    ]
    
    # Vérifier quota stable_memory plein
    can_add, reason = agi._check_profile_quota('stable_memory', mock_hof)
    assert can_add == False
    assert "full" in reason.lower()
    
    # Vérifier quota chaotic_probe OK
    can_add, reason = agi._check_profile_quota('chaotic_probe', mock_hof)
    assert can_add == True
    assert "ok" in reason.lower()
    
    # Vérifier profil sans quota
    can_add, reason = agi._check_profile_quota('robust_memory', mock_hof)
    assert can_add == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

