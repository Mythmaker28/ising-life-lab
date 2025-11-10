"""
Command-line tool for scanning CA/Ising rule spaces.

Usage:
    python -m isinglab.scan_rules --config experiments/scan_default.yaml
    python -m isinglab.scan_rules --rules 0 255 --output outputs/
"""

import argparse
import yaml
from pathlib import Path
from .search import RuleScanner


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scan CA/Ising rule space for edge-of-chaos and memory behavior"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML configuration file"
    )
    
    parser.add_argument(
        "--rules",
        type=int,
        nargs=2,
        metavar=("MIN", "MAX"),
        help="Rule range to scan (e.g., --rules 0 255)"
    )
    
    parser.add_argument(
        "--ca-type",
        type=str,
        default="elementary",
        choices=["elementary", "life", "totalistic"],
        help="Type of cellular automaton"
    )
    
    parser.add_argument(
        "--grid-size",
        type=int,
        nargs="+",
        default=[100, 100],
        help="Grid size (e.g., --grid-size 100 for 1D, --grid-size 100 100 for 2D)"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        default=200,
        help="Number of evolution steps"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=1,
        help="Number of different initial conditions per rule"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top rules to save separately"
    )
    
    parser.add_argument(
        "--metric",
        type=str,
        default="edge_score",
        help="Metric for ranking top rules"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for rule scanning."""
    args = parse_args()
    
    # Load configuration if provided
    if args.config:
        config = load_config(args.config)
        
        # Override with command-line args if provided
        rule_range = config.get("rule_range", [0, 255])
        ca_type = config.get("ca_type", "elementary")
        grid_size = config.get("grid_size", [100, 100])
        steps = config.get("steps", 200)
        seed = config.get("seed", 42)
        n_seeds = config.get("n_seeds", 1)
        output_dir = config.get("output_dir", "outputs")
        top_n = config.get("top_n", 20)
        metric = config.get("metric", "edge_score")
        verbose = config.get("verbose", True)
    else:
        # Use command-line arguments
        if args.rules is None:
            print("Error: Must provide --config or --rules")
            return
        
        rule_range = args.rules
        ca_type = args.ca_type
        grid_size = tuple(args.grid_size)
        steps = args.steps
        seed = args.seed
        n_seeds = args.n_seeds
        output_dir = args.output
        top_n = args.top_n
        metric = args.metric
        verbose = args.verbose
    
    # Create scanner
    scanner = RuleScanner(output_dir=output_dir, verbose=verbose)
    
    if verbose:
        print("=" * 60)
        print("ISING LIFE LAB - Rule Scanner")
        print("=" * 60)
        print(f"Configuration:")
        print(f"  Rule range: {rule_range[0]} - {rule_range[1]}")
        print(f"  CA type: {ca_type}")
        print(f"  Grid size: {grid_size}")
        print(f"  Steps: {steps}")
        print(f"  Seeds per rule: {n_seeds}")
        print(f"  Random seed: {seed}")
        print(f"  Output: {output_dir}")
        print("=" * 60)
    
    # Run scan
    if ca_type == "elementary":
        df = scanner.scan_elementary_ca(
            rule_subset=list(range(rule_range[0], rule_range[1] + 1)),
            grid_size=grid_size[0] if len(grid_size) == 1 else grid_size[0],
            steps=steps,
            seed=seed,
            n_seeds=n_seeds
        )
    else:
        df = scanner.scan_range(
            rule_range=range(rule_range[0], rule_range[1] + 1),
            grid_size=grid_size,
            steps=steps,
            seed=seed,
            ca_type=ca_type,
            n_seeds=n_seeds
        )
    
    # Save results
    scanner.save_results(
        df,
        filename="scan_results.csv",
        save_top=True,
        top_metric=metric,
        n_top=top_n
    )
    
    if verbose:
        print("\n" + "=" * 60)
        print("Scan complete!")
        print("=" * 60)
        print(f"\nResults summary:")
        print(f"  Total rules scanned: {len(df)}")
        print(f"  Mean edge_score: {df['edge_score'].mean():.4f}")
        print(f"  Max edge_score: {df['edge_score'].max():.4f}")
        print(f"\nFiles created:")
        print(f"  - {output_dir}/scan_results.csv")
        print(f"  - {output_dir}/top_rules.json")


if __name__ == "__main__":
    main()

