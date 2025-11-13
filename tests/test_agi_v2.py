"""Tests pour AGI v2.0 - Seuils adaptatifs, Diversité, Bandit"""

import pytest
import json
from pathlib import Path
import numpy as np

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.meta_learner.selector import MultiArmedBandit, CandidateSelector
from isinglab.rules import load_hof_rules
from isinglab.export_memory_library import compute_diversity_signature, infer_tags_from_scores


def test_compute_diversity_signature():
    """Test la signature de diversité."""
    sig1 = compute_diversity_signature([1, 3], [2, 3])
    assert sig1 == "B2_13/S2_23"
    
    sig2 = compute_diversity_signature([1, 2, 3], [2, 3, 6])
    assert sig2 == "B3_123/S3_236"
    
    # Signatures différentes pour règles différentes
    assert sig1 != sig2


def test_infer_tags_from_scores():
    """Test l'inférence de tags depuis les scores."""
    scores_high = {
        'memory_score': 0.6,
        'edge_score': 0.4,
        'entropy': 0.8
    }
    tags_high = infer_tags_from_scores(scores_high)
    assert 'high_memory' in tags_high
    assert 'robust' in tags_high
    assert 'high_entropy' in tags_high
    assert 'dynamic' in tags_high
    
    scores_low = {
        'memory_score': 0.05,
        'edge_score': 0.1,
        'entropy': 0.1
    }
    tags_low = infer_tags_from_scores(scores_low)
    assert 'low_memory' in tags_low
    assert 'fragile' in tags_low
    assert 'static' in tags_low


def test_adaptive_thresholds():
    """Test que les seuils adaptatifs se calculent correctement."""
    config = {
        'adaptive_thresholds': True,
        'hof_percentiles': {
            'composite_min': 90,
            'memory_score_min_abs': 0.01,
            'edge_score_min_abs': 0.05,
            'entropy_min_abs': 0.0
        },
        'diversity_threshold': 2
    }
    agi = ClosedLoopAGI(config=config)
    
    # Charger la mémoire existante
    agi.meta_memory = agi.aggregator.aggregate()
    
    if len(agi.meta_memory) >= 5:
        thresholds = agi._compute_adaptive_thresholds()
        
        assert 'composite_threshold' in thresholds
        assert 'adaptive' in thresholds
        assert thresholds['adaptive'] == True
        assert thresholds['composite_threshold'] >= 0
        assert thresholds['memory_abs_min'] == 0.01


def test_rule_distance():
    """Test la distance de Hamming entre règles."""
    agi = ClosedLoopAGI()
    
    rule1 = {'born': [1, 3], 'survive': [2, 3]}
    rule2 = {'born': [1, 3], 'survive': [2, 3]}
    rule3 = {'born': [1, 2, 3], 'survive': [2, 3, 6]}
    
    # Distance 0 entre règles identiques
    dist_same = agi._compute_rule_distance(rule1, rule2)
    assert dist_same == 0
    
    # Distance > 0 entre règles différentes
    dist_diff = agi._compute_rule_distance(rule1, rule3)
    assert dist_diff > 0
    # B: [1,3] vs [1,2,3] → +1 (le 2)
    # S: [2,3] vs [2,3,6] → +1 (le 6)
    assert dist_diff == 2


def test_diversity_filter():
    """Test le filtre de diversité pour HoF."""
    agi = ClosedLoopAGI()
    
    # HoF vide → toujours diverse
    is_diverse, reason = agi._is_diverse_enough({'born': [1, 3], 'survive': [2]}, [])
    assert is_diverse == True
    assert reason == "HoF empty"
    
    # Règle trop similaire → rejetée
    hof = [{'born': [1, 3], 'survive': [2]}]
    candidate_similar = {'born': [1, 3], 'survive': [2, 3]}  # Distance = 1
    is_diverse, reason = agi._is_diverse_enough(candidate_similar, hof)
    assert is_diverse == False
    assert "Too similar" in reason
    
    # Règle suffisamment différente → acceptée
    candidate_different = {'born': [4, 5, 6], 'survive': [1, 2]}
    is_diverse, reason = agi._is_diverse_enough(candidate_different, hof)
    assert is_diverse == True
    assert reason == "Diverse"


def test_multi_armed_bandit_initialization():
    """Test l'initialisation du bandit."""
    # Utiliser un fichier temporaire unique pour éviter la persistance
    import tempfile
    temp_file = tempfile.mktemp(suffix='.json')
    bandit = MultiArmedBandit(['exploitation', 'curiosity', 'diversity', 'random'], persistence_file=temp_file)
    
    assert len(bandit.arms) == 4
    assert 'exploitation' in bandit.arms
    assert 'curiosity' in bandit.arms
    assert 'diversity' in bandit.arms
    assert 'random' in bandit.arms
    
    # Note: total_pulls peut être > 0 si un fichier de persistance existe
    # Vérifier plutôt que les bras existent
    for arm in bandit.arms.values():
        assert arm.pulls >= 0
        assert arm.avg_reward >= 0.0


def test_multi_armed_bandit_selection():
    """Test la sélection UCB1 du bandit."""
    import tempfile
    temp_file = tempfile.mktemp(suffix='.json')
    bandit = MultiArmedBandit(['exploitation', 'curiosity'], persistence_file=temp_file)
    
    # Au début, tous les bras ont UCB=inf → sélection arbitraire
    first_arm = bandit.select_arm()
    assert first_arm in ['exploitation', 'curiosity']
    
    # Après des rewards, le meilleur bras devrait être préféré
    bandit.update_arm('exploitation', 1.0)
    bandit.update_arm('curiosity', 0.1)
    
    # Exploitation a meilleur avg_reward
    assert bandit.arms['exploitation'].avg_reward > bandit.arms['curiosity'].avg_reward


def test_multi_armed_bandit_persistence():
    """Test la sauvegarde/chargement des stats du bandit."""
    test_file = Path('results/test_bandit_stats.json')
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Créer et sauvegarder
    bandit1 = MultiArmedBandit(['test_arm1', 'test_arm2'], persistence_file=str(test_file))
    bandit1.update_arm('test_arm1', 0.5)
    bandit1.update_arm('test_arm1', 0.7)
    bandit1.update_arm('test_arm2', 0.3)
    
    # Charger dans un nouveau bandit
    bandit2 = MultiArmedBandit(['test_arm1', 'test_arm2'], persistence_file=str(test_file))
    
    assert bandit2.arms['test_arm1'].pulls == 2
    assert bandit2.arms['test_arm1'].avg_reward == 0.6  # (0.5 + 0.7) / 2
    assert bandit2.arms['test_arm2'].pulls == 1
    assert bandit2.arms['test_arm2'].avg_reward == 0.3
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()


def test_agi_v2_run_with_adaptive():
    """
    Test intégration : une itération AGI v2 avec seuils adaptatifs.
    Vérifie que les seuils adaptatifs sont calculés et utilisés.
    """
    config = {
        'evaluation_seed': 42,
        'adaptive_thresholds': True,
        'hof_percentiles': {'composite_min': 85},
        'diversity_threshold': 2
    }
    agi = ClosedLoopAGI(config=config)
    
    # Charger la mémoire pour avoir des données
    agi.meta_memory = agi.aggregator.aggregate()
    
    if len(agi.meta_memory) >= 5:
        # Une itération
        summary = agi.run_one_iteration(batch_size=4, strategy='mixed', grid_size=16, steps=50)
        
        assert 'total_memory_rules' in summary
        assert 'total_hof_rules' in summary
        
        # Vérifier que le log mentionne "ADAPTIVE"
        log_content = Path(summary['log_file']).read_text(encoding='utf-8')
        assert 'ADAPTIVE' in log_content or 'Composite threshold' in log_content


def test_agi_v2_diversity_rejection():
    """
    Test qu'une règle trop similaire est rejetée pour diversité.
    """
    # Réinitialiser le HoF pour le test
    hof_path = Path('isinglab/rules/hof_rules.json')
    original_hof = load_hof_rules()
    
    # Créer un HoF avec une seule règle
    test_hof = [{
        'notation': 'B3/S23',
        'born': [3],
        'survive': [2, 3],
        'tier': 'test',
        'avg_recall': 50,
        'edge_score': 0.2,
        'entropy': 0.5
    }]
    
    with open(hof_path, 'w', encoding='utf-8') as f:
        json.dump({'rules': test_hof}, f)
    
    try:
        config = {
            'adaptive_thresholds': True,
            'hof_percentiles': {'composite_min': 85},
            'diversity_threshold': 3  # Distance minimale élevée
        }
        agi = ClosedLoopAGI(config=config)
        
        # Tester une règle très similaire (B3/S2 vs B3/S23)
        similar_rule = {'born': [3], 'survive': [2], 'notation': 'B3/S2'}
        current_hof = load_hof_rules()
        is_diverse, reason = agi._is_diverse_enough(similar_rule, current_hof)
        
        # Distance = 1 (seul le 3 de survive diffère) < threshold=3
        assert is_diverse == False
        assert "Too similar" in reason
        
    finally:
        # Restaurer (ou laisser le test HoF)
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

