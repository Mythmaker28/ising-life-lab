"""Tests pour la capacité Life basée sur patterns canoniques.

Validation :
- B3/S23 (Life) doit avoir un score élevé
- Death rules doivent avoir un score nul/faible
- Autres règles intéressantes testées
"""

import pytest
import numpy as np
from isinglab.metrics.functional import compute_life_pattern_capacity
from isinglab.memory_explorer import MemoryExplorer


class TestLifePatternCapacity:
    """Tests métrique life_pattern_capacity."""
    
    def test_life_rule_high_score(self):
        """B3/S23 (Life) doit avoir un score élevé."""
        explorer = MemoryExplorer()
        rule_func = explorer._create_rule_function([3], [2, 3])
        
        result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
        
        score = result['life_capacity_score']
        patterns = result['patterns']
        
        # Life doit avoir un score > 0.5 (au moins certains patterns fonctionnent)
        assert score > 0.5, f"B3/S23 devrait avoir un score > 0.5, obtenu {score:.3f}"
        
        # Au moins le block (still life) doit survivre
        assert patterns['block']['survived'], "Block devrait survivre dans Life"
        
        # Au moins 3 patterns sur 5 devraient avoir un score > 0
        n_working = sum(1 for p in patterns.values() if p['score'] > 0.3)
        assert n_working >= 3, f"Au moins 3 patterns devraient fonctionner, obtenu {n_working}"
    
    def test_death_rule_low_score(self):
        """Death rules doivent avoir un score nul."""
        explorer = MemoryExplorer()
        rule_func = explorer._create_rule_function([], [8])  # B/S8 = death
        
        result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
        
        score = result['life_capacity_score']
        patterns = result['patterns']
        
        # Death rule doit avoir un score ~ 0
        assert score < 0.2, f"Death rule devrait avoir un score < 0.2, obtenu {score:.3f}"
        
        # Aucun pattern ne devrait survivre
        n_survived = sum(1 for p in patterns.values() if p['survived'])
        assert n_survived == 0, f"Aucun pattern ne devrait survivre dans death rule"
    
    def test_highlife_rule(self):
        """B36/S23 (HighLife) : comportement similaire à Life."""
        explorer = MemoryExplorer()
        rule_func = explorer._create_rule_function([3, 6], [2, 3])
        
        result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
        
        score = result['life_capacity_score']
        
        # HighLife devrait avoir un score raisonnable (> 0.3)
        # Peut être différent de Life à cause de B6
        assert score > 0.3, f"HighLife devrait avoir un score > 0.3, obtenu {score:.3f}"
    
    def test_pattern_structure(self):
        """Vérifie la structure des résultats."""
        explorer = MemoryExplorer()
        rule_func = explorer._create_rule_function([3], [2, 3])
        
        result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
        
        # Vérifier présence des clés
        assert 'life_capacity_score' in result
        assert 'patterns' in result
        assert 'n_patterns_tested' in result
        
        # Vérifier 5 patterns testés
        assert result['n_patterns_tested'] == 5
        assert len(result['patterns']) == 5
        
        # Vérifier structure par pattern
        for name, pattern_result in result['patterns'].items():
            assert 'score' in pattern_result
            assert 'survived' in pattern_result
            assert 'found_period' in pattern_result
            assert 'final_density' in pattern_result
            
            # Scores dans [0, 1]
            assert 0 <= pattern_result['score'] <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])




