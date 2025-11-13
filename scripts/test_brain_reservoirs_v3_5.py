"""
Test Brain Modules as Computational Reservoirs v3.5

Tâches:
1. N-bit memory (séquentiel): mémoriser une séquence de bits
2. Pattern denoising (spatial): reconstruire pattern bruité

Readout: Ridge regression linéaire
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import json
from datetime import datetime
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import train_test_split

from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized


BRAIN_MODULES = [
    "B3/S23", "B36/S23", "B3/S234",
    "B34/S34", "B36/S234",
    "B3/S2", "B23/S23", "B34/S234"
]


class CAReservoir:
    """Cellular Automaton as computational reservoir."""
    
    def __init__(self, notation, grid_size=(32, 32)):
        self.notation = notation
        self.grid_size = grid_size
        born, survive = parse_notation(notation)
        self.born_set = set(born)
        self.survive_set = set(survive)
        self.grid = None
    
    def reset(self, seed=42):
        """Reset reservoir to random initial state."""
        np.random.seed(seed)
        self.grid = (np.random.rand(*self.grid_size) < 0.3).astype(int)
    
    def step(self, external_input=None):
        """
        Evolve one step with optional external input.
        
        External input: (position, value) or None
        """
        if external_input is not None:
            pos, value = external_input
            self.grid[pos] = value
        
        self.grid = evolve_ca_vectorized(self.grid, self.born_set, self.survive_set, steps=1)
    
    def read_state(self):
        """Read current state as feature vector."""
        # Multiple readout strategies
        features = []
        
        # Global density
        features.append(self.grid.mean())
        
        # Quadrant densities
        h, w = self.grid_size
        features.append(self.grid[:h//2, :w//2].mean())
        features.append(self.grid[:h//2, w//2:].mean())
        features.append(self.grid[h//2:, :w//2].mean())
        features.append(self.grid[h//2:, w//2:].mean())
        
        # Edge density
        edge_mask = np.zeros(self.grid_size, dtype=bool)
        edge_mask[0, :] = edge_mask[-1, :] = edge_mask[:, 0] = edge_mask[:, -1] = True
        features.append(self.grid[edge_mask].mean())
        
        # Center density
        center_size = min(h//4, w//4)
        cx, cy = h//2, w//2
        features.append(self.grid[cx-center_size:cx+center_size, cy-center_size:cy+center_size].mean())
        
        # Activity measure (variance in local neighborhoods)
        from scipy.ndimage import uniform_filter
        local_avg = uniform_filter(self.grid.astype(float), size=3)
        features.append(np.var(local_avg))
        
        return np.array(features)


def task_n_bit_memory(reservoir, n_bits=4, n_samples=100, steps_per_bit=5):
    """
    Task: Memorize n-bit sequence.
    
    Input: sequence of bits (0 or 1)
    Output: recall the k-th bit
    """
    X_states = []
    y_targets = []
    
    for sample in range(n_samples):
        # Generate random bit sequence
        np.random.seed(42 + sample)
        bit_sequence = np.random.randint(0, 2, size=n_bits)
        
        reservoir.reset(seed=42 + sample)
        
        # Feed sequence into reservoir
        for bit_idx, bit in enumerate(bit_sequence):
            for step in range(steps_per_bit):
                # Inject bit at specific location
                input_pos = (reservoir.grid_size[0]//2, reservoir.grid_size[1]//2)
                reservoir.step(external_input=(input_pos, bit))
        
        # After full sequence, try to recall each bit
        for target_bit_idx in range(n_bits):
            state_features = reservoir.read_state()
            X_states.append(state_features)
            y_targets.append(bit_sequence[target_bit_idx])
            
            # Evolve a bit more (washout)
            for _ in range(2):
                reservoir.step()
    
    X = np.array(X_states)
    y = np.array(y_targets)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Logistic regression readout
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    return {
        'task': 'n_bit_memory',
        'n_bits': n_bits,
        'n_samples': n_samples,
        'train_accuracy': float(train_acc),
        'test_accuracy': float(test_acc)
    }


def task_pattern_denoising(reservoir, n_samples=50, noise_level=0.2, steps=10):
    """
    Task: Denoise a pattern.
    
    Input: noisy pattern
    Output: reconstructed clean pattern
    """
    X_states = []
    y_densities = []
    
    for sample in range(n_samples):
        np.random.seed(42 + sample)
        
        # Create clean pattern (simple shapes)
        clean_pattern = np.zeros(reservoir.grid_size, dtype=int)
        cx, cy = reservoir.grid_size[0]//2, reservoir.grid_size[1]//2
        
        # Random shape
        shape_type = sample % 3
        if shape_type == 0:
            # Block
            clean_pattern[cx-2:cx+2, cy-2:cy+2] = 1
        elif shape_type == 1:
            # Cross
            clean_pattern[cx-3:cx+3, cy] = 1
            clean_pattern[cx, cy-3:cy+3] = 1
        else:
            # Circle-ish
            for i in range(-3, 4):
                for j in range(-3, 4):
                    if i*i + j*j <= 9:
                        clean_pattern[cx+i, cy+j] = 1
        
        clean_density = clean_pattern.mean()
        
        # Add noise
        noisy_pattern = clean_pattern.copy()
        n_flips = int(reservoir.grid_size[0] * reservoir.grid_size[1] * noise_level)
        for _ in range(n_flips):
            i = np.random.randint(0, reservoir.grid_size[0])
            j = np.random.randint(0, reservoir.grid_size[1])
            noisy_pattern[i, j] = 1 - noisy_pattern[i, j]
        
        # Initialize reservoir with noisy pattern
        reservoir.grid = noisy_pattern.copy()
        
        # Evolve
        for _ in range(steps):
            reservoir.step()
        
        # Read final state
        state_features = reservoir.read_state()
        final_density = reservoir.grid.mean()
        
        X_states.append(state_features)
        y_densities.append(clean_density)
    
    X = np.array(X_states)
    y = np.array(y_densities)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Ridge regression readout
    model = Ridge(alpha=1.0, random_state=42)
    model.fit(X_train, y_train)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    # MAE
    from sklearn.metrics import mean_absolute_error
    train_mae = mean_absolute_error(y_train, model.predict(X_train))
    test_mae = mean_absolute_error(y_test, model.predict(X_test))
    
    return {
        'task': 'pattern_denoising',
        'n_samples': n_samples,
        'noise_level': noise_level,
        'train_r2': float(train_score),
        'test_r2': float(test_score),
        'train_mae': float(train_mae),
        'test_mae': float(test_mae)
    }


def test_reservoir(notation):
    """Test single reservoir on both tasks."""
    print(f"\n{'='*70}")
    print(f"Testing {notation}")
    print(f"{'='*70}")
    
    reservoir = CAReservoir(notation, grid_size=(32, 32))
    
    # Task 1: N-bit memory
    print("  Task 1: N-bit memory...")
    try:
        result_memory = task_n_bit_memory(reservoir, n_bits=3, n_samples=80, steps_per_bit=5)
        print(f"    Train acc: {result_memory['train_accuracy']:.3f}")
        print(f"    Test acc:  {result_memory['test_accuracy']:.3f}")
    except Exception as e:
        print(f"    ERROR: {e}")
        result_memory = {'error': str(e)}
    
    # Task 2: Pattern denoising
    print("  Task 2: Pattern denoising...")
    try:
        result_denoising = task_pattern_denoising(reservoir, n_samples=60, noise_level=0.25, steps=10)
        print(f"    Train R²: {result_denoising['train_r2']:.3f}")
        print(f"    Test R²:  {result_denoising['test_r2']:.3f}")
        print(f"    Test MAE: {result_denoising['test_mae']:.3f}")
    except Exception as e:
        print(f"    ERROR: {e}")
        result_denoising = {'error': str(e)}
    
    return {
        'notation': notation,
        'n_bit_memory': result_memory,
        'pattern_denoising': result_denoising
    }


def main():
    print("="*80)
    print("BRAIN MODULES AS COMPUTATIONAL RESERVOIRS v3.5")
    print("="*80)
    print()
    
    results = []
    
    for notation in BRAIN_MODULES:
        try:
            result = test_reservoir(notation)
            results.append(result)
        except Exception as e:
            print(f"\nERROR testing {notation}: {e}")
            results.append({
                'notation': notation,
                'error': str(e)
            })
    
    # Save results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_data = {
        'meta': {
            'version': '3.5',
            'date': datetime.now().isoformat(),
            'tasks': ['n_bit_memory', 'pattern_denoising']
        },
        'results': results
    }
    
    with open(output_dir / "brain_reservoirs_v3_5.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print("\nN-bit Memory Performance:")
    print("-" * 60)
    memory_results = [(r['notation'], r.get('n_bit_memory', {}).get('test_accuracy', 0)) 
                      for r in results if 'error' not in r]
    memory_results_sorted = sorted(memory_results, key=lambda x: x[1], reverse=True)
    
    for notation, acc in memory_results_sorted:
        print(f"  {notation:12s}: {acc:.3f}")
    
    print("\nPattern Denoising Performance:")
    print("-" * 60)
    denoising_results = [(r['notation'], r.get('pattern_denoising', {}).get('test_r2', 0))
                         for r in results if 'error' not in r]
    denoising_results_sorted = sorted(denoising_results, key=lambda x: x[1], reverse=True)
    
    for notation, r2 in denoising_results_sorted:
        print(f"  {notation:12s}: R²={r2:.3f}")
    
    print(f"\nResults saved: results/brain_reservoirs_v3_5.json")


if __name__ == "__main__":
    main()

