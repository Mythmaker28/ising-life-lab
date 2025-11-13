"""Closed Loop AGI v2.1 - modules mémoire exploitables avec Pareto"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

from isinglab.meta_learner import MemoryAggregator, train_meta_model, CandidateSelector
from isinglab.meta_learner.pareto import select_pareto_hof
from isinglab.rules import load_hof_rules, add_or_update_rule, save_hof_rules
from isinglab.memory_explorer import MemoryExplorer, parse_notation
from isinglab.metrics.functional import infer_module_profile


class ClosedLoopAGI:
    """Façade orchestrant la mémoire, le méta-modèle et l'exploration."""

    def __init__(self, config: Dict = None):
        self.config = config or {
            'evaluation_seed': 42,
            'use_pareto': False,  # v2.2: Désactivé au profit de quotas simples
            'profile_stability_min': 0.67,  # v2.2: Stabilité multi-grilles minimale
            'hof_profile_quotas': {  # v2.2: Quotas par profil
                'stable_memory': 4,
                'robust_memory': 4,
                'diverse_memory': 4,
                'chaotic_probe': 4,
                'sensitive_detector': 4,
                'attractor_dominant': 2,
                'generic': 2
            },
            'pareto_objectives': [  # v2.1: objectifs pour Pareto
                'functional_score',
                'memory_score',
                'edge_score',
                'entropy'
            ],
            'hof_max_size': 20,  # Taille max du HoF
            'adaptive_thresholds': True,  # v2.0: seuils adaptatifs
            'hof_percentiles': {
                'composite_min': 85,  # v2.2: Baissé de 90 à 85 pour plus de promotions
                'memory_score_min_abs': 0.01,
                'edge_score_min_abs': 0.05,
                'entropy_min_abs': 0.0
            },
            'diversity_threshold': 2,  # Distance Hamming minimale
            'hof_thresholds': {  # Fallback si tout désactivé
                'memory_score_min': 0.70,
                'edge_score_min': 0.20,
                'entropy_min': 0.30
            }
        }
        self.aggregator = MemoryAggregator()
        self.meta_memory: List[Dict] = []
        self.meta_model = None
        self.selector = None
        self.explorer = MemoryExplorer(output_dir='results/scans')

        Path('logs').mkdir(parents=True, exist_ok=True)
        self.log_file = Path('logs') / f"agi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def _log(self, message: str):
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')

    def _compute_adaptive_thresholds(self) -> Dict:
        """
        Calcule les seuils adaptatifs basés sur les percentiles des scores observés.
        Retourne les seuils calculés pour logging et décision.
        """
        if len(self.meta_memory) < 5:
            # Pas assez de données, utiliser les seuils fixes
            return self.config['hof_thresholds']
        
        # Extraire tous les scores
        memory_scores = []
        edge_scores = []
        entropy_scores = []
        composite_scores = []
        
        for rule in self.meta_memory:
            scores = rule.get('scores', {})
            mem = scores.get('memory_score')
            edge = scores.get('edge_score')
            ent = scores.get('entropy')
            
            if mem is not None:
                memory_scores.append(mem)
            if edge is not None:
                edge_scores.append(edge)
            if ent is not None:
                entropy_scores.append(ent)
            
            # Score composite : même formule que pour le bootstrap
            if mem is not None and edge is not None and ent is not None:
                composite = (mem * 0.5) + (edge * 0.3) + (ent * 0.2)
                composite_scores.append(composite)
        
        percentiles = self.config.get('hof_percentiles', {})
        composite_pct = percentiles.get('composite_min', 90)
        
        thresholds = {
            'composite_threshold': np.percentile(composite_scores, composite_pct) if composite_scores else 0,
            'memory_abs_min': percentiles.get('memory_score_min_abs', 0.01),
            'edge_abs_min': percentiles.get('edge_score_min_abs', 0.05),
            'entropy_abs_min': percentiles.get('entropy_min_abs', 0.0),
            'adaptive': True
        }
        
        return thresholds
    
    def _compute_rule_distance(self, rule1: Dict, rule2: Dict) -> int:
        """
        Distance de Hamming entre deux règles CA.
        Compte les différences dans born et survive.
        """
        born1 = set(rule1.get('born', []))
        born2 = set(rule2.get('born', []))
        survive1 = set(rule1.get('survive', []))
        survive2 = set(rule2.get('survive', []))
        
        # Différence symétrique = éléments dans l'un mais pas dans l'autre
        dist_born = len(born1 ^ born2)
        dist_survive = len(survive1 ^ survive2)
        
        return dist_born + dist_survive
    
    def _is_diverse_enough(self, candidate: Dict, hof_rules: List[Dict]) -> Tuple[bool, str]:
        """
        Vérifie si une règle candidate est suffisamment différente du HoF actuel.
        Retourne (is_diverse, reason).
        """
        if not hof_rules:
            return True, "HoF empty"
        
        min_distance = self.config.get('diversity_threshold', 2)
        
        for hof_rule in hof_rules:
            distance = self._compute_rule_distance(candidate, hof_rule)
            if distance < min_distance:
                return False, f"Too similar to {hof_rule.get('notation')} (dist={distance})"
        
        return True, "Diverse"
    
    def _check_profile_quota(self, profile: str, current_hof: List[Dict]) -> Tuple[bool, str]:
        """
        v2.2: Vérifie si le quota pour un profil est atteint.
        Retourne (can_add, reason).
        """
        quotas = self.config.get('hof_profile_quotas', {})
        if not quotas or profile not in quotas:
            return True, "No quota"
        
        # Compter profils actuels
        from collections import Counter
        profile_counts = Counter(r.get('module_profile', 'unknown') for r in current_hof)
        current_count = profile_counts.get(profile, 0)
        max_count = quotas.get(profile, 999)
        
        if current_count < max_count:
            return True, f"Quota OK ({current_count}/{max_count})"
        else:
            # Quota atteint : peut remplacer si meilleur
            return False, f"Quota full ({current_count}/{max_count})"

    def run_one_iteration(self, batch_size: int = 30, strategy: str = 'mixed', grid_size: int = 32, steps: int = 120):
        self._log('\n' + '=' * 64)
        self._log('CLOSED LOOP AGI v2.2 - ITERATION (STABLE-BIAS + QUOTAS)')
        self._log('=' * 64)

        # STEP 1 : mémoire agrégée (SANS réinitialiser !)
        self._log('\nSTEP 1: Aggregate memory')
        self.meta_memory = self.aggregator.aggregate()
        stats = self.aggregator.get_statistics()
        self._log(f"  Aggregated {stats.get('total_rules', 0)} rules")
        if stats.get('total_rules', 0) == 0:
            self._log("  [WARN] No rules in memory. Will bootstrap from evaluated candidates.")

        # STEP 2 : méta-modèle
        self._log('\nSTEP 2: Train meta-model')
        if len(self.meta_memory) >= 5:
            self.meta_model = train_meta_model(self.meta_memory)
            train_acc = self.meta_model.train_stats.get('train_accuracy', 0)
            test_acc = self.meta_model.train_stats.get('test_accuracy', 0)
            self._log(f"  Train acc: {train_acc:.2%}")
            self._log(f"  Test acc: {test_acc:.2%}")
        else:
            self.meta_model = None
            self._log('  Skipped (not enough data)')

        # STEP 3 : sélection de candidats (avec bandit si strategy='mixed')
        self._log('\nSTEP 3: Select candidates')
        if self.meta_model and self.meta_model.is_trained:
            self.selector = CandidateSelector(self.meta_model, self.meta_memory, use_bandit=True)
            candidates = self.selector.recommend_next_batch(pool_size=200, batch_size=batch_size, strategy=strategy)
            
            # Logger le bras choisi si bandit actif
            if strategy == 'mixed' and self.selector.last_arm_used:
                bandit_stats = self.selector.get_bandit_stats()
                self._log(f"  [BANDIT] Arm selected: {self.selector.last_arm_used}")
                if bandit_stats.get('arms'):
                    for arm_name, arm_data in bandit_stats['arms'].items():
                        pulls = arm_data['pulls']
                        avg = arm_data['avg_reward']
                        self._log(f"    - {arm_name}: pulls={pulls}, avg_reward={avg:.3f}")
            
            self._log(f"  {len(candidates)} candidates via strategy '{strategy}'")
        else:
            candidates = self._generate_neighbors_fallback(batch_size)
            self._log(f"  {len(candidates)} candidates via fallback neighbors")

        # STEP 4 : exploration effective
        self._log('\nSTEP 4: Explore candidates')
        eval_grid = (grid_size, grid_size)
        results = self.explorer.explore_batch(candidates, grid_size=eval_grid, steps=steps, seed=self.config['evaluation_seed'])
        evaluated = [r for r in results if 'error' not in r]
        self._log(f"  {len(evaluated)} / {len(results)} evaluated successfully")

        # STEP 5 : mise à jour mémoire + HoF (avec bootstrap si nécessaire)
        self._log('\nSTEP 5: Update memory & Hall of Fame')
        hof_added, bootstrapped = self._update_memory_and_hof(evaluated)
        if bootstrapped:
            self._log(f"  [BOOTSTRAP] {len(bootstrapped)} initial baseline(s) promoted")
        if hof_added:
            self._log(f"  [PROMOTED] {len(hof_added)} rules to HoF")
            for rule in hof_added:
                self._log(f"     - {rule['notation']} (composite={rule.get('composite_score', 0):.3f}, "
                          f"memory={rule.get('avg_recall', 0)/100:.3f}, edge={rule.get('edge_score', 0):.3f})")
        else:
            self._log(f"  [WARN] 0 rules promoted (thresholds not met)")
        
        # STEP 6 : mise à jour du bandit avec reward
        if self.selector and hasattr(self.selector, 'update_bandit_reward'):
            # Reward = nombre de promotions + qualité moyenne
            num_promotions = len(hof_added) + len(bootstrapped)
            avg_composite = np.mean([r.get('composite_score', 0) for r in evaluated]) if evaluated else 0
            reward = num_promotions + avg_composite  # Combinaison simple
            self.selector.update_bandit_reward(reward)
            self._log(f"  [BANDIT] Reward={reward:.3f} (promotions={num_promotions}, avg_composite={avg_composite:.3f})")

        total_hof = len(load_hof_rules())
        summary = {
            'candidates_tested': len(candidates),
            'results_obtained': len(evaluated),
            'new_rules_added': len(hof_added),
            'bootstrapped': len(bootstrapped) if bootstrapped else 0,
            'total_memory_rules': len(self.meta_memory),
            'total_hof_rules': total_hof,
            'strategy': strategy,
            'meta_model_accuracy': self.meta_model.train_stats.get('test_accuracy', 0) if self.meta_model else 0,
            'log_file': str(self.log_file)
        }

        self._log(f"\nSUMMARY: {summary}")
        return summary

    def _update_memory_and_hof(self, evaluated: List[Dict]):
        """
        v2.1: Met à jour la mémoire et le HoF avec sélection Pareto multi-objectif.
        Retourne (hof_added, bootstrapped).
        """
        added_rules = []
        bootstrapped = []
        removed_rules = []
        # rejected_diversity = []  # v2.1: à réimplémenter avec Pareto complet
        use_pareto = self.config.get('use_pareto', False)  # Désactivé temporairement
        
        # Calculer les seuils adaptatifs si activé
        use_adaptive = self.config.get('adaptive_thresholds', False)
        if use_adaptive:
            adaptive_thresholds = self._compute_adaptive_thresholds()
            self._log(f"  [ADAPTIVE] Composite threshold (p{self.config['hof_percentiles']['composite_min']}): "
                     f"{adaptive_thresholds['composite_threshold']:.4f}")
        else:
            adaptive_thresholds = None
        
        current_hof = load_hof_rules()
        
        # Partie 1: Mise à jour de la méta-mémoire avec toutes les métriques
        for res in evaluated:
            notation = res['notation']
            born = res.get('born') or parse_notation(notation)[0]
            survive = res.get('survive') or parse_notation(notation)[1]

            # v2.1: Toutes les métriques (classiques + fonctionnelles)
            memory_score = res.get('memory_score', 0)
            edge_score = res.get('edge_score', 0)
            entropy = res.get('entropy', 0)
            functional_score = res.get('functional_score', 0)
            capacity_score = res.get('capacity_score', 0)
            robustness_score = res.get('robustness_score', 0)
            basin_diversity = res.get('basin_diversity', 0.5)
            
            # Score composite (fallback)
            composite_score = (memory_score * 0.5) + (edge_score * 0.3) + (entropy * 0.2)

            normalized = self.aggregator.normalize_rule_entry({
                'notation': notation,
                'born': born,
                'survive': survive,
                'memory_score': memory_score,
                'edge_score': edge_score,
                'entropy': entropy,
                'tags': ['evaluated', 'closed_loop'],
                'discovered_date': datetime.now().strftime('%Y-%m-%d')
            }, source='closed_loop_iteration')
            
            # Ajouter métriques fonctionnelles v2.1
            normalized['scores']['functional_score'] = functional_score
            normalized['scores']['capacity_score'] = capacity_score
            normalized['scores']['robustness_score'] = robustness_score
            normalized['scores']['basin_diversity'] = basin_diversity

            # Ajouter times_evaluated pour éviter les boucles
            existing = next((rule for rule in self.meta_memory if rule['notation'] == notation), None)
            if existing:
                existing['scores'].update(normalized['scores'])
                existing['labels'] = sorted(set(existing['labels']) | set(normalized['labels']))
                existing['metadata']['times_evaluated'] = existing['metadata'].get('times_evaluated', 0) + 1
                existing['metadata']['last_seen_iter'] = datetime.now().isoformat()
            else:
                normalized['metadata']['times_evaluated'] = 1
                normalized['metadata']['last_seen_iter'] = datetime.now().isoformat()
                self.meta_memory.append(normalized)

            # v2.0: Évaluation pour promotion au HoF (seuils adaptatifs + diversité)
            promote = False
            reason = ""
            
            if use_adaptive and adaptive_thresholds:
                # Mode adaptatif : composite dans le top X% + bornes minimales
                composite_ok = composite_score >= adaptive_thresholds['composite_threshold']
                memory_ok = memory_score >= adaptive_thresholds['memory_abs_min']
                edge_ok = edge_score >= adaptive_thresholds['edge_abs_min']
                entropy_ok = entropy >= adaptive_thresholds['entropy_abs_min']
                
                # v2.3: Seuil absolu functional_score pour bypass percentile
                functional_ok = functional_score >= 0.30
                
                if (composite_ok or functional_ok) and memory_ok and edge_ok and entropy_ok:
                    # Inférer profil pour vérifier quota v2.2
                    from .metrics.functional import infer_module_profile
                    temp_profile, _ = infer_module_profile(
                        capacity=capacity_score,
                        robustness=robustness_score,
                        basin_diversity=basin_diversity,
                        entropy=entropy
                    )
                    
                    # Vérifier quota profil
                    can_add_profile, quota_reason = self._check_profile_quota(temp_profile, current_hof)
                    
                    if can_add_profile:
                        # Vérifier la diversité
                        candidate_rule = {'notation': notation, 'born': born, 'survive': survive}
                        is_diverse, diversity_reason = self._is_diverse_enough(candidate_rule, current_hof)
                        
                        if is_diverse:
                            promote = True
                            reason = f"adaptive ({temp_profile}, composite={composite_score:.3f})"
                        # else:
                        #     rejected_diversity.append((notation, diversity_reason))
                    else:
                        self._log(f"  [QUOTA] {notation} ({temp_profile}): {quota_reason}")
            else:
                # Mode fixe (fallback)
                fixed_thresholds = self.config['hof_thresholds']
                if (memory_score >= fixed_thresholds['memory_score_min'] and
                        edge_score >= fixed_thresholds['edge_score_min'] and
                        entropy >= fixed_thresholds['entropy_min']):
                    promote = True
                    reason = "fixed thresholds"
            
            if promote:
                # v2.2: Inférer et stocker module_profile
                from .metrics.functional import infer_module_profile
                module_profile, suggested_use = infer_module_profile(
                    capacity=capacity_score,
                    robustness=robustness_score,
                    basin_diversity=basin_diversity,
                    entropy=entropy
                )
                
                rule_data = {
                    'notation': notation,
                    'born': born,
                    'survive': survive,
                    'tier': 'adaptive_candidate',
                    'avg_recall': memory_score * 100,
                    'edge_score': edge_score,
                    'entropy': entropy,
                    'composite_score': composite_score,
                    'functional_score': functional_score,
                    'capacity_score': capacity_score,
                    'robustness_score': robustness_score,
                    'module_profile': module_profile,
                    'suggested_use': suggested_use,
                    'discovered_by': 'closed_loop_agi_v2.2',
                    'discovered_date': datetime.now().strftime('%Y-%m-%d'),
                    'tags': ['agi', 'automated', 'adaptive'],
                    'promotion_reason': reason
                }
                if add_or_update_rule(rule_data):
                    added_rules.append(rule_data)
                    current_hof.append(rule_data)  # Pour les checks de diversité suivants

        # BOOTSTRAP : si HoF vide ET des résultats évalués, promouvoir la meilleure règle
        current_hof = load_hof_rules()
        if len(current_hof) == 0 and len(evaluated) > 0:
            self._log("  [BOOTSTRAP MODE] HoF is empty, promoting best candidate as baseline...")
            # Trouver la meilleure règle du batch
            best_candidate = max(evaluated, key=lambda r: (
                (r.get('memory_score', 0) * 0.5) + 
                (r.get('edge_score', 0) * 0.3) + 
                (r.get('entropy', 0) * 0.2)
            ))
            notation = best_candidate['notation']
            born = best_candidate.get('born') or parse_notation(notation)[0]
            survive = best_candidate.get('survive') or parse_notation(notation)[1]
            composite = ((best_candidate.get('memory_score', 0) * 0.5) + 
                        (best_candidate.get('edge_score', 0) * 0.3) + 
                        (best_candidate.get('entropy', 0) * 0.2))
            
            bootstrap_rule = {
                'notation': notation,
                'born': born,
                'survive': survive,
                'tier': 'bootstrap',
                'avg_recall': best_candidate.get('memory_score', 0) * 100,
                'edge_score': best_candidate.get('edge_score', 0),
                'entropy': best_candidate.get('entropy', 0),
                'composite_score': composite,
                'discovered_by': 'closed_loop_agi_bootstrap',
                'discovered_date': datetime.now().strftime('%Y-%m-%d'),
                'tags': ['agi', 'automated', 'bootstrap', 'hof']
            }
            add_or_update_rule(bootstrap_rule)
            bootstrapped.append(bootstrap_rule)

        # Logging des rejets de diversité (v2.1: TODO avec Pareto complet)
        # if rejected_diversity:
        #     self._log(f"  [DIVERSITY] {len(rejected_diversity)} candidates rejected for similarity:")
        #     for notation, reason in rejected_diversity[:3]:
        #         self._log(f"     - {notation}: {reason}")
        
        # Sauvegarder la mémoire mise à jour
        self.aggregator.meta_memory = self.meta_memory
        self.aggregator.save()
        
        return added_rules, bootstrapped

    def _generate_neighbors_fallback(self, count: int) -> List[Dict]:
        hof = load_hof_rules()
        champions = [r for r in hof if r.get('tier') in {'champion', 'validated', 'candidate'}]
        candidates: List[Dict] = []
        for champ in champions:
            notation = champ['notation']
            neighbors = self.explorer.generate_neighbors(notation, radius=1)
            candidates.extend(neighbors)
            if len(candidates) >= count:
                break
        if not candidates:
            candidates = self.explorer.generate_random_candidates(count=count, seed=self.config['evaluation_seed'])
        return candidates[:count]


__all__ = ['ClosedLoopAGI']
