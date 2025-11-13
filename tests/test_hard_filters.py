"""Tests pour les filtres durs (filters.py) — v3.1

Validation :
- Cerveaux validés passent les filtres
- Death rules sont bloquées
- Saturation rules sont bloquées
"""

import pytest
from isinglab.meta_learner.filters import (
    apply_hard_filters,
    is_quasi_death_rule,
    is_saturation_rule
)


class TestHardFilters:
    """Tests filtres durs anti-trivialité."""
    
    def test_brains_pass_filters(self):
        """Les 3 cerveaux validés doivent passer les filtres."""
        brains = [
            'B3/S23',    # Life
            'B36/S23',   # HighLife
            'B34/S34'    # 34 Life
        ]
        
        for notation in brains:
            passed, reason = apply_hard_filters(notation)
            assert passed, f"{notation} devrait passer les filtres (raison: {reason})"
    
    def test_death_rule_blocked(self):
        """Quasi-death rules doivent être bloquées."""
        death_rules = [
            'B/S8',      # Death totale (density=0)
            'B/S0',      # Quasi-death (density=0.012)
        ]
        
        for notation in death_rules:
            is_death, reason = is_quasi_death_rule(notation)
            assert is_death, f"{notation} devrait être détectée comme quasi-death (reason: {reason})"
            
            passed, _ = apply_hard_filters(notation)
            assert not passed, f"{notation} ne devrait PAS passer apply_hard_filters"
    
    def test_saturation_rule_blocked(self):
        """Saturation rules doivent être bloquées."""
        saturation_rules = [
            'B0123456/S012345678',  # Saturation totale
        ]
        
        for notation in saturation_rules:
            is_sat, reason = is_saturation_rule(notation)
            assert is_sat, f"{notation} devrait être détectée comme saturation"
            
            passed, _ = apply_hard_filters(notation)
            assert not passed, f"{notation} ne devrait PAS passer apply_hard_filters"
    
    def test_candidate_b3_s234_passes(self):
        """B3/S234 doit passer les filtres (candidat intéressant)."""
        notation = 'B3/S234'
        passed, reason = apply_hard_filters(notation)
        assert passed, f"B3/S234 devrait passer (raison rejet: {reason})"
    
    def test_filter_reason_informative(self):
        """Les raisons de rejet doivent être claires."""
        notation = 'B/S8'  # Death rule
        passed, reason = apply_hard_filters(notation)
        assert not passed, f"B/S8 devrait être rejetée"
        assert 'death' in reason.lower() or 'density' in reason.lower(), \
            f"La raison de rejet doit mentionner 'death' ou 'density', reçu: {reason}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

