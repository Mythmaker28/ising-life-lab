"""
Rule Scanner - Systematic exploration of rule space.

Provides exhaustive or sampled scanning of CA/Ising rule spaces
with configurable metrics and output formats.
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable
from ..api import evaluate_batch


class RuleScanner:
    """
    Systematic scanner for CA rule spaces.
    
    Allows:
    - Exhaustive scanning (all rules in range)
    - Random sampling (Monte Carlo)
    - Configurable evaluation parameters
    - Automatic result saving
    """
    
    def __init__(
        self,
        output_dir: str = "outputs",
        verbose: bool = True
    ):
        """
        Initialize scanner.
        
        Args:
            output_dir: Directory to save results
            verbose: Print progress messages
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.verbose = verbose
        
    def scan_range(
        self,
        rule_range: Union[range, List[int]],
        grid_size: tuple = (100, 100),
        steps: int = 200,
        seed: int = 42,
        ca_type: str = "elementary",
        n_seeds: int = 1,
        filter_func: Optional[Callable] = None
    ) -> pd.DataFrame:
        """
        Scan a range of rules.
        
        Args:
            rule_range: Range or list of rules to scan
            grid_size: Grid dimensions
            steps: Evolution steps
            seed: Base random seed
            ca_type: CA type
            n_seeds: Repetitions per rule with different seeds
            filter_func: Optional function to pre-filter rules
            
        Returns:
            DataFrame with all metrics
        """
        if self.verbose:
            print(f"Scanning {len(rule_range)} rules...")
        
        # Filter rules if specified
        if filter_func is not None:
            rules = [r for r in rule_range if filter_func(r)]
            if self.verbose:
                print(f"After filtering: {len(rules)} rules")
        else:
            rules = list(rule_range)
        
        # Evaluate all rules
        results = evaluate_batch(
            rules=rules,
            grid_size=grid_size,
            steps=steps,
            seed=seed,
            ca_type=ca_type,
            n_seeds=n_seeds
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        if self.verbose:
            print(f"Scan complete. {len(df)} rules evaluated.")
        
        return df
    
    def scan_elementary_ca(
        self,
        rule_subset: Optional[List[int]] = None,
        grid_size: int = 100,
        steps: int = 200,
        seed: int = 42,
        n_seeds: int = 3
    ) -> pd.DataFrame:
        """
        Scan elementary CA rules (Wolfram rules 0-255).
        
        Args:
            rule_subset: If provided, only scan these rules
            grid_size: 1D grid size
            steps: Evolution steps
            seed: Random seed
            n_seeds: Repetitions per rule
            
        Returns:
            DataFrame with metrics
        """
        if rule_subset is None:
            rule_range = range(256)
        else:
            rule_range = rule_subset
        
        return self.scan_range(
            rule_range=rule_range,
            grid_size=(grid_size,),
            steps=steps,
            seed=seed,
            ca_type="elementary",
            n_seeds=n_seeds
        )
    
    def scan_life_like(
        self,
        rules: Optional[List[int]] = None,
        grid_size: tuple = (100, 100),
        steps: int = 200,
        seed: int = 42,
        n_seeds: int = 3
    ) -> pd.DataFrame:
        """
        Scan Life-like CA rules.
        
        Args:
            rules: List of Life-like rules (encoded)
            grid_size: 2D grid size
            steps: Evolution steps
            seed: Random seed
            n_seeds: Repetitions per rule
            
        Returns:
            DataFrame with metrics
        """
        if rules is None:
            # Default: scan common Life-like rules
            rules = self._generate_life_rules()
        
        return self.scan_range(
            rule_range=rules,
            grid_size=grid_size,
            steps=steps,
            seed=seed,
            ca_type="life",
            n_seeds=n_seeds
        )
    
    def _generate_life_rules(self, n_samples: int = 100) -> List[int]:
        """Generate sample of Life-like rules."""
        # Sample birth and survival conditions
        rules = []
        for _ in range(n_samples):
            birth = np.random.choice(range(9), size=np.random.randint(1, 5), replace=False)
            survival = np.random.choice(range(9), size=np.random.randint(1, 5), replace=False)
            
            # Encode as integer
            rule = 0
            for b in birth:
                rule |= (1 << b)
            for s in survival:
                rule |= (1 << (s + 9))
            
            rules.append(rule)
        
        return list(set(rules))  # Remove duplicates
    
    def find_top_rules(
        self,
        df: pd.DataFrame,
        metric: str = "edge_score",
        n_top: int = 10,
        min_value: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Extract top rules by specified metric.
        
        Args:
            df: Results DataFrame
            metric: Metric to sort by
            n_top: Number of top rules to return
            min_value: Minimum value threshold
            
        Returns:
            DataFrame with top rules
        """
        if metric not in df.columns:
            raise ValueError(f"Metric '{metric}' not found in results")
        
        # Filter by minimum value if specified
        if min_value is not None:
            df = df[df[metric] >= min_value]
        
        # Sort and take top n
        top_df = df.sort_values(by=metric, ascending=False).head(n_top)
        
        if self.verbose:
            print(f"\nTop {len(top_df)} rules by {metric}:")
            for idx, row in top_df.iterrows():
                print(f"  Rule {row['rule']}: {metric}={row[metric]:.4f}")
        
        return top_df
    
    def save_results(
        self,
        df: pd.DataFrame,
        filename: str = "scan_results.csv",
        save_top: bool = True,
        top_metric: str = "edge_score",
        n_top: int = 20
    ):
        """
        Save scan results to disk.
        
        Args:
            df: Results DataFrame
            filename: CSV filename
            save_top: Also save top rules as JSON
            top_metric: Metric for selecting top rules
            n_top: Number of top rules to save separately
        """
        # Save full results
        csv_path = self.output_dir / filename
        df.to_csv(csv_path, index=False)
        
        if self.verbose:
            print(f"\nResults saved to: {csv_path}")
        
        # Save top rules
        if save_top:
            top_df = self.find_top_rules(df, metric=top_metric, n_top=n_top)
            
            top_rules = []
            for _, row in top_df.iterrows():
                rule_dict = row.to_dict()
                # Convert numpy types to native Python types for JSON
                rule_dict = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                           for k, v in rule_dict.items()}
                top_rules.append(rule_dict)
            
            json_path = self.output_dir / "top_rules.json"
            with open(json_path, 'w') as f:
                json.dump(top_rules, f, indent=2)
            
            if self.verbose:
                print(f"Top {n_top} rules saved to: {json_path}")
    
    def load_results(self, filename: str = "scan_results.csv") -> pd.DataFrame:
        """Load previous scan results."""
        csv_path = self.output_dir / filename
        return pd.read_csv(csv_path)

