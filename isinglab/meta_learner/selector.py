"""Candidate selection strategies using the meta-model v2.0 with Multi-Armed Bandit."""

import random
import math
from typing import Dict, List, Tuple
from pathlib import Path
import json

from isinglab.memory_explorer import parse_notation


class BanditArm:
    """Un bras du bandit multi-armed."""
    
    def __init__(self, name: str):
        self.name = name
        self.pulls = 0
        self.total_reward = 0.0
        self.avg_reward = 0.0
    
    def update(self, reward: float):
        """Met à jour les stats après une récompense."""
        self.pulls += 1
        self.total_reward += reward
        self.avg_reward = self.total_reward / self.pulls
    
    def compute_ucb(self, total_pulls: int, c: float = 1.4) -> float:
        """Calcule l'Upper Confidence Bound."""
        if self.pulls == 0:
            return float('inf')  # Toujours essayer les bras jamais testés
        exploration_bonus = c * math.sqrt(math.log(total_pulls) / self.pulls)
        return self.avg_reward + exploration_bonus
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'pulls': self.pulls,
            'total_reward': self.total_reward,
            'avg_reward': self.avg_reward
        }


class MultiArmedBandit:
    """
    Gestion des stratégies d'exploration avec UCB1.
    Choisit dynamiquement la meilleure stratégie.
    """
    
    def __init__(self, arms: List[str], persistence_file: str = 'results/bandit_stats.json'):
        self.arms = {name: BanditArm(name) for name in arms}
        self.total_pulls = 0
        self.persistence_file = Path(persistence_file)
        self.load_stats()
    
    def select_arm(self) -> str:
        """Sélectionne un bras selon UCB1."""
        ucb_scores = {name: arm.compute_ucb(self.total_pulls) for name, arm in self.arms.items()}
        best_arm = max(ucb_scores, key=ucb_scores.get)
        return best_arm
    
    def update_arm(self, arm_name: str, reward: float):
        """Met à jour les stats d'un bras."""
        if arm_name in self.arms:
            self.arms[arm_name].update(reward)
            self.total_pulls += 1
            self.save_stats()
    
    def get_stats(self) -> Dict:
        """Retourne les stats pour logging."""
        return {
            'total_pulls': self.total_pulls,
            'arms': {name: arm.to_dict() for name, arm in self.arms.items()}
        }
    
    def load_stats(self):
        """Charge les stats depuis le fichier."""
        if not self.persistence_file.exists():
            return
        try:
            with open(self.persistence_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.total_pulls = data.get('total_pulls', 0)
            arms_data = data.get('arms', {})
            for name, arm_data in arms_data.items():
                if name in self.arms:
                    self.arms[name].pulls = arm_data.get('pulls', 0)
                    self.arms[name].total_reward = arm_data.get('total_reward', 0.0)
                    self.arms[name].avg_reward = arm_data.get('avg_reward', 0.0)
        except Exception:
            pass
    
    def save_stats(self):
        """Sauvegarde les stats dans le fichier."""
        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_stats(), f, indent=2)


class CandidateSelector:
    def __init__(self, meta_model, meta_memory: List[Dict], use_bandit: bool = True):
        self.meta_model = meta_model
        self.meta_memory = meta_memory
        self.use_bandit = use_bandit
        
        # Initialiser le bandit avec 5 bras (+ stable_bias v2.2)
        if use_bandit:
            self.bandit = MultiArmedBandit(['exploitation', 'curiosity', 'diversity', 'random', 'stable_bias'])
            self.last_arm_used = None
        else:
            self.bandit = None
            self.last_arm_used = None

    def recommend_next_batch(self, pool_size: int = 200, batch_size: int = 30, strategy: str = 'mixed') -> List[Dict]:
        pool = self._build_candidate_pool(pool_size)
        if not pool:
            return []

        # v2.0: Si strategy='mixed' et bandit activé, utiliser UCB1
        if strategy == 'mixed' and self.use_bandit and self.bandit:
            arm = self.bandit.select_arm()
            self.last_arm_used = arm
            return self._select_by_arm(pool, arm, batch_size)
        
        # Fallback sur les stratégies fixes
        if strategy == 'exploitation':
            self.last_arm_used = 'exploitation'
            return self._select_by_arm(pool, 'exploitation', batch_size)
        if strategy == 'exploration':
            self.last_arm_used = 'curiosity'
            return self._select_by_arm(pool, 'curiosity', batch_size)
        if strategy == 'diversity':
            self.last_arm_used = 'diversity'
            return self._diversity_sampling(pool, batch_size)
        if strategy == 'random':
            self.last_arm_used = 'random'
            return self._select_by_arm(pool, 'random', batch_size)
        
        # Fallback par défaut (ancien mixed)
        self.last_arm_used = 'mixed_fallback'
        top = sorted(pool, key=lambda c: c['score'], reverse=True)[:max(5, batch_size // 2)]
        exploratory = sorted(pool, key=lambda c: abs(c['score'] - 0.5))[:batch_size // 3]
        diverse = self._diversity_sampling(pool, batch_size - len(top) - len(exploratory))
        combined = (top + exploratory + diverse)[:batch_size]
        seen = set()
        unique = []
        for cand in combined:
            if cand['notation'] not in seen:
                unique.append(cand)
                seen.add(cand['notation'])
        return unique
    
    def _select_by_arm(self, pool: List[Dict], arm: str, batch_size: int) -> List[Dict]:
        """Sélectionne des candidats selon la stratégie du bras."""
        if arm == 'exploitation':
            # Top scores prédits
            ranked = sorted(pool, key=lambda c: c['score'], reverse=True)
            return ranked[:batch_size]
        
        elif arm == 'curiosity':
            # Candidats incertains (proche de 0.5)
            ranked = sorted(pool, key=lambda c: abs(c['score'] - 0.5))
            return ranked[:batch_size]
        
        elif arm == 'diversity':
            # Diversité par born_count
            return self._diversity_sampling(pool, batch_size)
        
        elif arm == 'random':
            # Échantillonnage aléatoire
            return random.sample(pool, min(batch_size, len(pool)))
        
        elif arm == 'stable_bias':
            # v2.2: Générateur biaisé vers règles stables (Born petit, Survive ⊃ {2,3})
            return self._generate_stable_biased_candidates(batch_size)
        
        else:
            # Fallback
            return pool[:batch_size]
    
    def update_bandit_reward(self, reward: float):
        """
        Met à jour le reward du dernier bras utilisé.
        À appeler après évaluation des candidats.
        """
        if self.use_bandit and self.bandit and self.last_arm_used:
            self.bandit.update_arm(self.last_arm_used, reward)
    
    def get_bandit_stats(self) -> Dict:
        """Retourne les stats du bandit pour logging."""
        if self.use_bandit and self.bandit:
            return self.bandit.get_stats()
        return {}

    # ------------------------------------------------------------------
    def _diversity_sampling(self, pool: List[Dict], batch_size: int) -> List[Dict]:
        if batch_size <= 0:
            return []
        buckets: Dict[int, List[Dict]] = {}
        for cand in pool:
            born_count = len(cand.get('born', []))
            buckets.setdefault(born_count, []).append(cand)
        selected: List[Dict] = []
        while len(selected) < batch_size and buckets:
            for born_count in sorted(buckets.keys()):
                if buckets[born_count]:
                    selected.append(buckets[born_count].pop(0))
                    if len(selected) >= batch_size:
                        break
                else:
                    buckets.pop(born_count, None)
        return selected

    def _build_candidate_pool(self, pool_size: int) -> List[Dict]:
        """
        Construit un pool de candidats avec pénalisation des règles déjà testées.
        Évite les boucles stériles en favorisant de nouvelles règles.
        """
        # Construire un index des règles déjà évaluées avec leur fréquence
        evaluated_counts = {}
        for entry in self.meta_memory:
            notation = entry.get('notation')
            times = entry.get('metadata', {}).get('times_evaluated', 0)
            if notation:
                evaluated_counts[notation] = times
        
        base_rules = [entry for entry in self.meta_memory if entry.get('notation')]
        # Trier pour favoriser les règles peu évaluées ou jamais vues
        base_rules.sort(key=lambda e: e.get('metadata', {}).get('times_evaluated', 0))
        
        pool: List[Dict] = []
        seen = set()

        for entry in base_rules:
            notation = entry.get('notation')
            try:
                born, survive = parse_notation(notation)
            except ValueError:
                continue
            mutations = self._mutate_rule(born, survive)
            for born_mut, survive_mut in mutations:
                candidate_notation = f"B{''.join(map(str, born_mut))}/S{''.join(map(str, survive_mut))}"
                if candidate_notation in seen:
                    continue
                
                # Prédiction du méta-modèle (si disponible)
                if self.meta_model:
                    score = self.meta_model.predict_proba(
                        notation=candidate_notation,
                        born=born_mut,
                        survive=survive_mut
                    )
                else:
                    score = 0.5  # Score neutre si pas de modèle
                
                # Pénalisation si déjà évalué plusieurs fois
                penalty_factor = 0.15  # 15% de pénalité par évaluation
                times_eval = evaluated_counts.get(candidate_notation, 0)
                adjusted_score = score * (1.0 - penalty_factor * times_eval)
                
                pool.append({
                    'notation': candidate_notation,
                    'born': born_mut,
                    'survive': survive_mut,
                    'score': adjusted_score,
                    'raw_score': score,
                    'times_evaluated': times_eval,
                    'source': 'meta_model'
                })
                seen.add(candidate_notation)
                if len(pool) >= pool_size:
                    return pool
        # fallback random completions
        while len(pool) < pool_size:
            born_mut = sorted(random.sample(range(9), random.randint(1, 4)))
            survive_mut = sorted(random.sample(range(9), random.randint(1, 4)))
            candidate_notation = f"B{''.join(map(str, born_mut))}/S{''.join(map(str, survive_mut))}"
            if candidate_notation in seen:
                continue
            # Score via meta_model si disponible, sinon défaut
            if self.meta_model:
                score = self.meta_model.predict_proba(
                    notation=candidate_notation,
                    born=born_mut,
                    survive=survive_mut
                )
            else:
                score = 0.5  # Score neutre si pas de modèle
            pool.append({
                'notation': candidate_notation,
                'born': born_mut,
                'survive': survive_mut,
                'score': score,
                'source': 'random_fill'
            })
            seen.add(candidate_notation)
        return pool

    def _generate_stable_biased_candidates(self, count: int) -> List[Dict]:
        """
        v2.2: Génère des candidats biaisés vers stabilité/mémoire.
        
        Contraintes:
        - Born ⊂ {0, 1, 2, 3} (max 2 valeurs)
        - Survive contient {2} ou {3} (ou les deux)
        - Voisinage de B3/S23 (Game of Life)
        """
        candidates = []
        seen = set()
        
        # Base : voisins de B3/S23 (Life) - Born ⊂ {0,1,2,3}
        life_variants = [
            ([3], [2, 3]),      # Game of Life
            ([2, 3], [2, 3]),   # HighLife variant
            ([3], [2]),
            ([3], [3]),
            ([1, 3], [2, 3]),
            ([2, 3], [3]),
            ([3], [1, 2, 3]),
            ([3], [2, 3, 4]),
            ([0, 3], [2, 3]),
            ([1, 2], [2, 3]),
        ]
        
        for born, survive in life_variants:
            notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
            if notation not in seen:
                candidates.append({
                    'notation': notation,
                    'born': born,
                    'survive': survive,
                    'score': 0.7,  # Score élevé pour favoriser sélection
                    'source': 'stable_bias'
                })
                seen.add(notation)
                if len(candidates) >= count:
                    return candidates
        
        # Compléter avec génération contrôlée
        while len(candidates) < count:
            # Born : 1-2 valeurs dans {0,1,2,3}
            born_size = random.choice([1, 2])
            born = sorted(random.sample([0, 1, 2, 3], born_size))
            
            # Survive : doit contenir 2 ou 3
            survive_base = [random.choice([2, 3])]
            # Ajouter 1-2 valeurs supplémentaires
            survive_extra = random.sample([x for x in range(5) if x not in survive_base], random.randint(0, 2))
            survive = sorted(survive_base + survive_extra)
            
            notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
            if notation not in seen:
                candidates.append({
                    'notation': notation,
                    'born': born,
                    'survive': survive,
                    'score': 0.6,
                    'source': 'stable_bias'
                })
                seen.add(notation)
        
        return candidates[:count]
    
    def _mutate_rule(self, born: List[int], survive: List[int]) -> List[Tuple[List[int], List[int]]]:
        mutations: List[Tuple[List[int], List[int]]] = []
        for b in range(9):
            if b not in born:
                new_born = sorted(born + [b])
                mutations.append((new_born, survive))
            elif len(born) > 1:
                new_born = [x for x in born if x != b]
                mutations.append((new_born, survive))
        for s in range(9):
            if s not in survive:
                new_survive = sorted(survive + [s])
                mutations.append((born, new_survive))
            elif len(survive) > 1:
                new_survive = [x for x in survive if x != s]
                mutations.append((born, new_survive))
        return mutations


__all__ = ['CandidateSelector']
