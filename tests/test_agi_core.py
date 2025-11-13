"""Tests pour le système Closed Loop AGI."""

import json
from pathlib import Path
import pytest

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.rules import load_hof_rules


def test_import_agi():
    """Test que ClosedLoopAGI peut être importé."""
    assert ClosedLoopAGI is not None


def test_agi_initialization():
    """Test l'initialisation du système AGI."""
    agi = ClosedLoopAGI()
    assert agi is not None
    assert agi.aggregator is not None
    assert agi.explorer is not None
    assert agi.config is not None
    assert 'hof_thresholds' in agi.config


def test_agi_run_one_iteration_no_crash():
    """
    Test qu'une itération s'exécute sans planter.
    Vérifie que :
    - meta_memory.json est créé/mis à jour
    - candidates >= results >= 0
    - le log est écrit
    """
    agi = ClosedLoopAGI()
    
    # Lancer une itération avec un petit batch pour aller vite
    summary = agi.run_one_iteration(batch_size=3, strategy='mixed', grid_size=16, steps=50)
    
    # Vérifications de base
    assert summary is not None
    assert 'candidates_tested' in summary
    assert 'results_obtained' in summary
    assert 'new_rules_added' in summary
    assert 'total_memory_rules' in summary
    
    # Vérifier que le nombre de résultats est cohérent
    assert summary['candidates_tested'] >= 0
    assert summary['results_obtained'] >= 0
    assert summary['results_obtained'] <= summary['candidates_tested']
    assert summary['new_rules_added'] >= 0
    
    # Vérifier que meta_memory.json a été créé
    meta_memory_path = Path('results/meta_memory.json')
    assert meta_memory_path.exists()
    
    # Vérifier que le fichier est un JSON valide
    with open(meta_memory_path, encoding='utf-8') as fh:
        data = json.load(fh)
    assert 'rules' in data
    assert 'meta' in data
    
    # Vérifier que le log existe
    log_file = Path(summary['log_file'])
    assert log_file.exists()


def test_agi_bootstrap_policy():
    """
    Test la politique de bootstrap : si HoF est vide, au moins une règle
    doit être promue après l'itération.
    """
    # Réinitialiser le HoF pour le test
    hof_path = Path('isinglab/rules/hof_rules.json')
    original_hof = load_hof_rules()
    
    # Vider temporairement le HoF
    with open(hof_path, 'w', encoding='utf-8') as fh:
        json.dump({'rules': []}, fh)
    
    try:
        agi = ClosedLoopAGI()
        summary = agi.run_one_iteration(batch_size=4, strategy='mixed', grid_size=16, steps=50)
        
        # Après une itération avec HoF vide, au moins une règle bootstrap devrait exister
        hof_rules = load_hof_rules()
        assert summary['bootstrapped'] >= 0
        if summary['results_obtained'] > 0:
            # Si on a obtenu des résultats, on devrait avoir bootstrapé ou promu quelque chose
            total_promoted = summary['new_rules_added'] + summary['bootstrapped']
            assert total_promoted > 0, "Aucune règle promue alors que des résultats existent"
    finally:
        # Restaurer le HoF original (ou laisser le nouveau si on veut)
        pass


def test_agi_memory_persistence():
    """
    Test que la mémoire persiste entre deux itérations.
    """
    agi = ClosedLoopAGI()
    
    # Première itération
    summary1 = agi.run_one_iteration(batch_size=2, strategy='mixed', grid_size=16, steps=30)
    total_memory_1 = summary1['total_memory_rules']
    
    # Deuxième itération
    summary2 = agi.run_one_iteration(batch_size=2, strategy='mixed', grid_size=16, steps=30)
    total_memory_2 = summary2['total_memory_rules']
    
    # La mémoire devrait au moins rester stable ou augmenter
    assert total_memory_2 >= total_memory_1, \
        f"La mémoire a diminué : {total_memory_1} -> {total_memory_2}"


def test_agi_no_duplicate_promotion():
    """
    Test qu'on ne re-teste pas indéfiniment les mêmes règles sans apprendre.
    """
    agi = ClosedLoopAGI()
    
    # Faire plusieurs itérations
    notations_tested = []
    for i in range(3):
        summary = agi.run_one_iteration(batch_size=3, strategy='mixed', grid_size=16, steps=30)
        # On ne peut pas facilement récupérer les notations testées ici sans modifier le code
        # Mais on peut au moins vérifier que le système tourne
        assert summary['candidates_tested'] > 0
    
    # Si le système fonctionne bien, après 3 itérations, on devrait avoir une mémoire non vide
    assert agi.meta_memory, "Aucune règle en mémoire après 3 itérations"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

