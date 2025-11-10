"""
Evolutionary search for optimal CA/Ising rules.

Uses genetic algorithms to discover rules with desired properties
(e.g., maximal edge-of-chaos score, specific memory characteristics).
"""

import numpy as np
from typing import List, Dict, Callable, Optional, Tuple
from ..api import evaluate_rule


class EvolutionarySearch:
    """
    Evolutionary/genetic algorithm for CA rule discovery.
    
    Evolves a population of rules toward a specified fitness objective.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_fraction: float = 0.1,
        seed: Optional[int] = None
    ):
        """
        Initialize evolutionary search.
        
        Args:
            population_size: Number of rules in population
            mutation_rate: Probability of bit flip per position
            crossover_rate: Probability of crossover between parents
            elite_fraction: Fraction of top rules to preserve unchanged
            seed: Random seed
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = max(1, int(population_size * elite_fraction))
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        self.population = []
        self.fitness_history = []
        
    def initialize_population(self, rule_type: str = "elementary") -> List[int]:
        """
        Create initial random population.
        
        Args:
            rule_type: "elementary" (8-bit) or "life" (18-bit)
            
        Returns:
            List of random rules
        """
        if rule_type == "elementary":
            max_rule = 255
        elif rule_type == "life":
            max_rule = (1 << 18) - 1
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")
        
        self.population = [np.random.randint(0, max_rule + 1) 
                          for _ in range(self.population_size)]
        
        return self.population
    
    def evaluate_population(
        self,
        fitness_func: Callable[[int], float],
        **eval_kwargs
    ) -> List[Tuple[int, float]]:
        """
        Evaluate fitness of all individuals.
        
        Args:
            fitness_func: Function that takes rule and eval_kwargs, returns fitness
            eval_kwargs: Additional arguments for evaluation
            
        Returns:
            List of (rule, fitness) tuples, sorted by fitness
        """
        fitnesses = []
        
        for rule in self.population:
            # Evaluate rule
            fitness = fitness_func(rule, **eval_kwargs)
            fitnesses.append((rule, fitness))
        
        # Sort by fitness (descending)
        fitnesses.sort(key=lambda x: x[1], reverse=True)
        
        return fitnesses
    
    def select_parents(
        self,
        fitnesses: List[Tuple[int, float]],
        n_parents: int
    ) -> List[int]:
        """
        Select parents for next generation using tournament selection.
        
        Args:
            fitnesses: List of (rule, fitness) tuples
            n_parents: Number of parents to select
            
        Returns:
            List of selected parent rules
        """
        parents = []
        
        for _ in range(n_parents):
            # Tournament selection (size 3)
            tournament = np.random.choice(len(fitnesses), size=3, replace=False)
            best_idx = min(tournament)  # fitnesses is already sorted
            parents.append(fitnesses[best_idx][0])
        
        return parents
    
    def crossover(self, parent1: int, parent2: int, n_bits: int = 8) -> Tuple[int, int]:
        """
        Single-point crossover between two rules.
        
        Args:
            parent1, parent2: Parent rules
            n_bits: Number of bits in rule representation
            
        Returns:
            Two offspring rules
        """
        if np.random.rand() > self.crossover_rate:
            return parent1, parent2
        
        # Random crossover point
        point = np.random.randint(1, n_bits)
        mask = (1 << point) - 1
        
        offspring1 = (parent1 & ~mask) | (parent2 & mask)
        offspring2 = (parent2 & ~mask) | (parent1 & mask)
        
        return offspring1, offspring2
    
    def mutate(self, rule: int, n_bits: int = 8) -> int:
        """
        Bit-flip mutation.
        
        Args:
            rule: Rule to mutate
            n_bits: Number of bits
            
        Returns:
            Mutated rule
        """
        for bit in range(n_bits):
            if np.random.rand() < self.mutation_rate:
                rule ^= (1 << bit)  # Flip bit
        
        return rule
    
    def evolve_generation(
        self,
        fitnesses: List[Tuple[int, float]],
        rule_type: str = "elementary"
    ) -> List[int]:
        """
        Create next generation via selection, crossover, and mutation.
        
        Args:
            fitnesses: Current population with fitness scores
            rule_type: Type of rule (determines bit length)
            
        Returns:
            New population
        """
        n_bits = 8 if rule_type == "elementary" else 18
        
        # Elitism: keep top individuals
        elite = [rule for rule, _ in fitnesses[:self.elite_size]]
        
        # Generate offspring
        offspring = []
        n_offspring_needed = self.population_size - self.elite_size
        
        while len(offspring) < n_offspring_needed:
            # Select parents
            parents = self.select_parents(fitnesses, 2)
            
            # Crossover
            child1, child2 = self.crossover(parents[0], parents[1], n_bits)
            
            # Mutation
            child1 = self.mutate(child1, n_bits)
            child2 = self.mutate(child2, n_bits)
            
            offspring.extend([child1, child2])
        
        # Trim to exact size
        offspring = offspring[:n_offspring_needed]
        
        # New population
        new_population = elite + offspring
        
        return new_population
    
    def run(
        self,
        fitness_func: Callable[[int], float],
        n_generations: int = 100,
        rule_type: str = "elementary",
        verbose: bool = True,
        **eval_kwargs
    ) -> Dict:
        """
        Run evolutionary search.
        
        Args:
            fitness_func: Fitness function (takes rule, returns score)
            n_generations: Number of generations to evolve
            rule_type: "elementary" or "life"
            verbose: Print progress
            eval_kwargs: Additional arguments for fitness function
            
        Returns:
            Dictionary with:
            - best_rule: Best rule found
            - best_fitness: Its fitness score
            - fitness_history: Fitness over generations
            - final_population: Final population
        """
        # Initialize
        self.initialize_population(rule_type)
        self.fitness_history = []
        
        for generation in range(n_generations):
            # Evaluate
            fitnesses = self.evaluate_population(fitness_func, **eval_kwargs)
            
            # Track best
            best_rule, best_fitness = fitnesses[0]
            mean_fitness = np.mean([f for _, f in fitnesses])
            self.fitness_history.append({
                "generation": generation,
                "best_fitness": best_fitness,
                "mean_fitness": mean_fitness,
                "best_rule": best_rule
            })
            
            if verbose and generation % 10 == 0:
                print(f"Gen {generation}: Best={best_fitness:.4f}, Mean={mean_fitness:.4f}, Rule={best_rule}")
            
            # Evolve next generation
            if generation < n_generations - 1:
                self.population = self.evolve_generation(fitnesses, rule_type)
        
        # Final evaluation
        final_fitnesses = self.evaluate_population(fitness_func, **eval_kwargs)
        best_rule, best_fitness = final_fitnesses[0]
        
        return {
            "best_rule": best_rule,
            "best_fitness": best_fitness,
            "fitness_history": self.fitness_history,
            "final_population": [rule for rule, _ in final_fitnesses]
        }


def edge_fitness(rule: int, **eval_kwargs) -> float:
    """
    Fitness function optimizing for edge-of-chaos.
    
    Args:
        rule: CA rule number
        eval_kwargs: Arguments for evaluate_rule
        
    Returns:
        Fitness score (edge_score)
    """
    try:
        metrics = evaluate_rule(rule=rule, **eval_kwargs)
        return metrics["edge_score"]
    except Exception:
        # Invalid rule or evaluation failed
        return 0.0


def memory_fitness(rule: int, **eval_kwargs) -> float:
    """
    Fitness function optimizing for memory behavior.
    
    Args:
        rule: CA rule number
        eval_kwargs: Arguments for evaluate_rule
        
    Returns:
        Fitness score (memory_score)
    """
    try:
        metrics = evaluate_rule(rule=rule, **eval_kwargs)
        return metrics["memory_score"]
    except Exception:
        return 0.0

