"""
Tests de calibration des métriques v3.4

Valide que les métriques distinguent correctement :
- Brain modules (B3/S23, B36/S23, etc.)
- Stabilizers (B/S234, B/S123)
- Sinks (B6/S23)

NOTE v9.0: Ces tests concernent CA historiques (branche close).
Marqués pour skip car non prioritaires pour toolkit v8+.
"""

import pytest

# Skip all CA historical tests (branche close v7.0)
pytestmark = pytest.mark.skip(reason="CA-reservoir branch closed, historical tests only")
import numpy as np
from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized
from isinglab.metrics.functional import (
    compute_life_pattern_capacity,
    compute_robustness_to_noise,
    compute_basin_size
)
from isinglab.meta_learner.filters import apply_hard_filters


def create_rule_func(notation):
    """Helper to create rule function."""
    born, survive = parse_notation(notation)
    born_set, survive_set = set(born), set(survive)
    
    def rule_func(grid):
        return evolve_ca_vectorized(grid, born_set, survive_set, steps=1)
    
    return rule_func


def classify_rule(notation):
    """Simplified classification for testing."""
    born, survive = parse_notation(notation)
    
    # Structural check
    if not born:
        return {'category': 'stabilizer', 'reason': 'No birth rules'}
    
    # Hard filters
    passed_filters, reason = apply_hard_filters(notation)
    if not passed_filters:
        return {'category': 'sink', 'reason': reason}
    
    # Compute metrics
    rule_func = create_rule_func(notation)
    
    life_result = compute_life_pattern_capacity(rule_func, grid_size=(48, 48))
    life_score = life_result['life_capacity_score']
    
    rob_result = compute_robustness_to_noise(
        rule_func, grid_size=(32, 32), noise_level=0.2, n_trials=2, steps=50
    )
    robustness = rob_result['robustness_score']
    
    basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=8, steps=50)
    diversity = basin_result['basin_diversity']
    
    # Classification logic
    if robustness > 0.9 and life_score < 0.3:
        category = 'stabilizer'
        reason = f'Perfect robustness ({robustness:.2f}) but low capacity ({life_score:.2f})'
    elif life_score > 0.5:
        category = 'brain_module'
        reason = f'High life_capacity={life_score:.2f}'
    elif life_score > 0.4 and diversity > 0.3:
        category = 'brain_module'
        reason = f'Good capacity ({life_score:.2f}) + diversity ({diversity:.2f})'
    else:
        category = 'unclassified'
        reason = 'Mixed metrics'
    
    return {
        'notation': notation,
        'category': category,
        'reason': reason,
        'life_capacity_score': life_score,
        'robustness': robustness,
        'basin_diversity': diversity
    }


class TestStabilizerRejection:
    """Tests que les stabilizers (born vide) sont rejetés."""
    
    def test_b_empty_s234_is_stabilizer(self):
        """B/S234 doit être classé stabilizer (born vide)."""
        result = classify_rule("B/S234")
        
        assert result['category'] == 'stabilizer', \
            f"B/S234 should be stabilizer, got {result['category']}"
        
        assert result['life_capacity_score'] < 0.2, \
            f"B/S234 should have low life capacity, got {result['life_capacity_score']}"
    
    def test_b_empty_s123_is_stabilizer(self):
        """B/S123 doit être classé stabilizer (born vide)."""
        result = classify_rule("B/S123")
        
        assert result['category'] == 'stabilizer', \
            f"B/S123 should be stabilizer, got {result['category']}"
        
        assert result['life_capacity_score'] < 0.2, \
            f"B/S123 should have low life capacity, got {result['life_capacity_score']}"


class TestQuasiDeathDetection:
    """Tests que les quasi-death rules sont détectées comme sinks."""
    
    def test_b6_s23_is_sink(self):
        """B6/S23 doit être détecté comme sink (quasi-death)."""
        result = classify_rule("B6/S23")
        
        # Hard filters should catch this
        assert result['category'] == 'sink', \
            f"B6/S23 should be sink, got {result['category']}"
        
        assert 'quasi-death' in result['reason'].lower() or 'death' in result['reason'].lower(), \
            f"B6/S23 reason should mention quasi-death, got: {result['reason']}"


class TestBrainValidation:
    """Tests que les cerveaux connus sont validés."""
    
    def test_life_b3s23_is_brain(self):
        """B3/S23 (Life) doit être validé comme brain_module."""
        result = classify_rule("B3/S23")
        
        assert result['category'] == 'brain_module', \
            f"B3/S23 should be brain_module, got {result['category']}"
        
        assert result['life_capacity_score'] > 0.5, \
            f"B3/S23 should have high life capacity, got {result['life_capacity_score']:.3f}"
    
    def test_highlife_b36s23_is_brain(self):
        """B36/S23 (HighLife) doit être validé comme brain_module."""
        result = classify_rule("B36/S23")
        
        assert result['category'] == 'brain_module', \
            f"B36/S23 should be brain_module, got {result['category']}"
        
        assert result['life_capacity_score'] > 0.5, \
            f"B36/S23 should have high life capacity, got {result['life_capacity_score']:.3f}"
    
    def test_b3s234_is_brain(self):
        """B3/S234 doit être validé comme brain_module."""
        result = classify_rule("B3/S234")
        
        assert result['category'] == 'brain_module', \
            f"B3/S234 should be brain_module, got {result['category']}"
        
        assert result['life_capacity_score'] > 0.4, \
            f"B3/S234 should have decent life capacity, got {result['life_capacity_score']:.3f}"


class TestLifePatternCapacity:
    """Tests spécifiques sur life_pattern_capacity."""
    
    def test_life_preserves_patterns(self):
        """B3/S23 doit préserver la majorité des patterns Life."""
        rule_func = create_rule_func("B3/S23")
        result = compute_life_pattern_capacity(rule_func, grid_size=(48, 48))
        
        # Life should preserve 4/5 patterns (glider is partial)
        assert result['life_capacity_score'] > 0.6, \
            f"Life should preserve most patterns, got {result['life_capacity_score']:.3f}"
        
        # Block should survive perfectly
        assert result['patterns']['block']['survived'], \
            "Block should survive in Life"
        
        # Blinker should survive
        assert result['patterns']['blinker']['survived'], \
            "Blinker should survive in Life"
    
    def test_born_empty_kills_patterns(self):
        """B/S234 ne doit PAS préserver les patterns Life (born vide)."""
        rule_func = create_rule_func("B/S234")
        result = compute_life_pattern_capacity(rule_func, grid_size=(48, 48))
        
        # Born empty cannot preserve oscillators (no birth)
        assert result['life_capacity_score'] < 0.3, \
            f"B/S234 should not preserve Life patterns, got {result['life_capacity_score']:.3f}"
        
        # Blinker should die (cannot oscillate without birth)
        assert not result['patterns']['blinker']['survived'] or \
               result['patterns']['blinker']['score'] < 0.5, \
            "Blinker should not survive properly in B/S234 (no birth for oscillation)"


class TestMetricsConsistency:
    """Tests de cohérence des métriques."""
    
    def test_robustness_not_sufficient_alone(self):
        """Robustesse élevée seule ne fait pas un brain module."""
        # Test avec une règle stabilizer à robustesse élevée
        result = classify_rule("B/S234")
        
        # Même si robustness est élevé, life_capacity doit primer
        if result.get('robustness', 0) > 0.8:
            assert result['category'] != 'brain_module', \
                "High robustness alone should not make a brain_module"
    
    def test_life_capacity_is_discriminative(self):
        """Life capacity doit discriminer brain vs stabilizer."""
        brain_result = classify_rule("B3/S23")
        stabilizer_result = classify_rule("B/S234")
        
        brain_capacity = brain_result['life_capacity_score']
        stabilizer_capacity = stabilizer_result['life_capacity_score']
        
        assert brain_capacity > stabilizer_capacity + 0.3, \
            f"Brain capacity ({brain_capacity:.3f}) should be significantly higher than " \
            f"stabilizer capacity ({stabilizer_capacity:.3f})"


class TestHardFilters:
    """Tests des filtres durs."""
    
    def test_quasi_death_filter_works(self):
        """Filtre quasi-death doit bloquer B6/S23."""
        passed, reason = apply_hard_filters("B6/S23")
        
        assert not passed, \
            f"B6/S23 should be blocked by hard filters, got passed={passed}"
        
        assert 'death' in reason.lower(), \
            f"Reason should mention death, got: {reason}"
    
    def test_valid_brain_passes_filters(self):
        """Les cerveaux valides doivent passer les filtres durs."""
        for brain in ["B3/S23", "B36/S23", "B3/S234"]:
            passed, reason = apply_hard_filters(brain)
            
            assert passed, \
                f"{brain} should pass hard filters, got blocked: {reason}"


if __name__ == "__main__":
    # Run with: pytest tests/test_metrics_calibration_v3_4.py -v
    pytest.main([__file__, "-v"])


