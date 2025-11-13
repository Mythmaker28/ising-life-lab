"""
Express version: Fewer samples for faster execution.
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
    "B34/S34", "B36/S234"
]


class CAReservoir:
    def __init__(self, notation, grid_size=(24, 24)):
        self.notation = notation
        self.grid_size = grid_size
        born, survive = parse_notation(notation)
        self.born_set = set(born)
        self.survive_set = set(survive)
        self.grid = None
    
    def reset(self, seed=42):
        np.random.seed(seed)
        self.grid = (np.random.rand(*self.grid_size) < 0.3).astype(int)
    
    def step(self, external_input=None):
        if external_input is not None:
            pos, value = external_input
            self.grid[pos] = value
        
        self.grid = evolve_ca_vectorized(self.grid, self.born_set, self.survive_set, steps=1)
    
    def read_state(self):
        features = []
        features.append(self.grid.mean())
        
        h, w = self.grid_size
        features.append(self.grid[:h//2, :w//2].mean())
        features.append(self.grid[:h//2, w//2:].mean())
        features.append(self.grid[h//2:, :w//2].mean())
        features.append(self.grid[h//2:, w//2:].mean())
        
        return np.array(features)


def task_n_bit_memory(reservoir, n_bits=3, n_samples=40, steps_per_bit=3):
    X_states = []
    y_targets = []
    
    for sample in range(n_samples):
        np.random.seed(42 + sample)
        bit_sequence = np.random.randint(0, 2, size=n_bits)
        
        reservoir.reset(seed=42 + sample)
        
        for bit_idx, bit in enumerate(bit_sequence):
            for step in range(steps_per_bit):
                input_pos = (reservoir.grid_size[0]//2, reservoir.grid_size[1]//2)
                reservoir.step(external_input=(input_pos, bit))
        
        for target_bit_idx in range(n_bits):
            state_features = reservoir.read_state()
            X_states.append(state_features)
            y_targets.append(bit_sequence[target_bit_idx])
            
            for _ in range(2):
                reservoir.step()
    
    X = np.array(X_states)
    y = np.array(y_targets)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X_train, y_train)
    
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    return {
        'task': 'n_bit_memory',
        'train_accuracy': float(train_acc),
        'test_accuracy': float(test_acc)
    }


def task_pattern_denoising(reservoir, n_samples=30, noise_level=0.25, steps=8):
    X_states = []
    y_densities = []
    
    for sample in range(n_samples):
        np.random.seed(42 + sample)
        
        clean_pattern = np.zeros(reservoir.grid_size, dtype=int)
        cx, cy = reservoir.grid_size[0]//2, reservoir.grid_size[1]//2
        
        shape_type = sample % 3
        if shape_type == 0:
            clean_pattern[cx-2:cx+2, cy-2:cy+2] = 1
        elif shape_type == 1:
            clean_pattern[cx-3:cx+3, cy] = 1
            clean_pattern[cx, cy-3:cy+3] = 1
        else:
            for i in range(-3, 4):
                for j in range(-3, 4):
                    if i*i + j*j <= 9:
                        clean_pattern[cx+i, cy+j] = 1
        
        clean_density = clean_pattern.mean()
        
        noisy_pattern = clean_pattern.copy()
        n_flips = int(reservoir.grid_size[0] * reservoir.grid_size[1] * noise_level)
        for _ in range(n_flips):
            i = np.random.randint(0, reservoir.grid_size[0])
            j = np.random.randint(0, reservoir.grid_size[1])
            noisy_pattern[i, j] = 1 - noisy_pattern[i, j]
        
        reservoir.grid = noisy_pattern.copy()
        
        for _ in range(steps):
            reservoir.step()
        
        state_features = reservoir.read_state()
        
        X_states.append(state_features)
        y_densities.append(clean_density)
    
    X = np.array(X_states)
    y = np.array(y_densities)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    model = Ridge(alpha=1.0, random_state=42)
    model.fit(X_train, y_train)
    
    test_score = model.score(X_test, y_test)
    
    from sklearn.metrics import mean_absolute_error
    test_mae = mean_absolute_error(y_test, model.predict(X_test))
    
    return {
        'task': 'pattern_denoising',
        'test_r2': float(test_score),
        'test_mae': float(test_mae)
    }


def test_reservoir(notation):
    print(f"\nTesting {notation}...", flush=True)
    
    reservoir = CAReservoir(notation, grid_size=(24, 24))
    
    try:
        result_memory = task_n_bit_memory(reservoir, n_bits=3, n_samples=40, steps_per_bit=3)
        print(f"  Memory: {result_memory['test_accuracy']:.3f}", flush=True)
    except Exception as e:
        result_memory = {'error': str(e)}
    
    try:
        result_denoising = task_pattern_denoising(reservoir, n_samples=30, noise_level=0.25, steps=8)
        print(f"  Denoise: R²={result_denoising['test_r2']:.3f}", flush=True)
    except Exception as e:
        result_denoising = {'error': str(e)}
    
    return {
        'notation': notation,
        'n_bit_memory': result_memory,
        'pattern_denoising': result_denoising
    }


def main():
    print("EXPRESS RESERVOIR TESTS v3.5")
    print("="*60, flush=True)
    
    results = []
    
    for notation in BRAIN_MODULES:
        try:
            result = test_reservoir(notation)
            results.append(result)
        except Exception as e:
            print(f"ERROR {notation}: {e}", flush=True)
            results.append({'notation': notation, 'error': str(e)})
    
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_data = {
        'meta': {
            'version': '3.5_express',
            'date': datetime.now().isoformat()
        },
        'results': results
    }
    
    with open(output_dir / "brain_reservoirs_v3_5.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for r in results:
        if 'error' in r:
            continue
        notation = r['notation']
        mem_acc = r.get('n_bit_memory', {}).get('test_accuracy', 0)
        den_r2 = r.get('pattern_denoising', {}).get('test_r2', 0)
        print(f"{notation:12s}: mem={mem_acc:.3f}, denoise_R²={den_r2:.3f}")
    
    print(f"\nSaved: results/brain_reservoirs_v3_5.json", flush=True)


if __name__ == "__main__":
    main()

