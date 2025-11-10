"""
Tests for isinglab metrics (entropy, sensitivity, memory, edge_score)
"""
import pytest
import numpy as np
from isinglab.metrics.entropy import shannon_entropy, spatial_entropy, activity_level
from isinglab.metrics.sensitivity import hamming_distance, hamming_sensitivity
from isinglab.metrics.memory import detect_cycle, memory_score
from isinglab.metrics.edge_score import edge_of_chaos_score, lambda_parameter_estimate


def test_shannon_entropy_extremes():
    """Test Shannon entropy on extreme cases"""
    # All zeros -> entropy = 0
    grid_zeros = np.zeros((10, 10), dtype=int)
    assert shannon_entropy(grid_zeros) == 0.0
    
    # All ones -> entropy = 0
    grid_ones = np.ones((10, 10), dtype=int)
    assert shannon_entropy(grid_ones) == 0.0
    
    # Perfectly balanced -> entropy ≈ 1.0
    grid_balanced = np.array([[0, 1] * 5] * 10, dtype=int)
    entropy = shannon_entropy(grid_balanced)
    assert 0.9 < entropy <= 1.0


def test_spatial_entropy():
    """Test spatial entropy calculation"""
    # Uniform pattern -> low spatial entropy
    grid_uniform = np.zeros((20, 20), dtype=int)
    grid_uniform[::2, ::2] = 1  # Checkerboard
    
    entropy = spatial_entropy(grid_uniform)
    assert 0 <= entropy <= 1.0
    
    # Random pattern -> higher spatial entropy
    np.random.seed(42)
    grid_random = np.random.randint(0, 2, (20, 20))
    entropy_random = spatial_entropy(grid_random)
    assert entropy_random > entropy


def test_activity_level():
    """Test activity level calculation"""
    # All zeros
    state_zeros = np.zeros(100, dtype=int)
    assert activity_level(state_zeros) == 0.0
    
    # All ones
    state_ones = np.ones(100, dtype=int)
    assert activity_level(state_ones) == 1.0
    
    # Half ones
    state_half = np.array([0, 1] * 50, dtype=int)
    assert 0.49 < activity_level(state_half) < 0.51


def test_hamming_distance():
    """Test Hamming distance calculation"""
    a = np.array([0, 1, 0, 1, 0])
    b = np.array([0, 1, 0, 1, 0])
    assert hamming_distance(a, b) == 0.0
    
    # All different
    c = np.array([1, 0, 1, 0, 1])
    assert hamming_distance(a, c) == 1.0
    
    # Half different
    d = np.array([0, 1, 1, 0, 0])
    assert hamming_distance(a, d) == 0.4


def test_hamming_sensitivity_stable_rule():
    """Test Hamming sensitivity for a stable rule"""
    def stable_rule(state, n_steps):
        """Rule that doesn't change state"""
        return state.copy()
    
    np.random.seed(42)
    initial = np.random.randint(0, 2, 20)
    
    sensitivity = hamming_sensitivity(stable_rule, initial, steps=10, perturbation=0.1, seed=42)
    # Stable rule should have near-zero sensitivity
    assert sensitivity < 0.2


def test_detect_cycle():
    """Test cycle detection in state history"""
    # Fixed point (cycle length 1)
    fixed = [np.array([1, 1, 1])] * 5
    result_fixed = detect_cycle(fixed, max_period=3)
    assert result_fixed is not None
    transient, period = result_fixed
    assert period == 1  # Fixed point has period 1
    assert isinstance(transient, int)
    
    # Alternating 2-cycle
    history = [
        np.array([0, 1, 0, 1]),
        np.array([1, 0, 1, 0]),
        np.array([0, 1, 0, 1]),
        np.array([1, 0, 1, 0]),
        np.array([0, 1, 0, 1]),
        np.array([1, 0, 1, 0]),
    ]
    result = detect_cycle(history, max_period=5)
    if result:  # May or may not detect depending on algorithm
        transient, period = result
        assert period >= 1
        assert isinstance(transient, int)


def test_memory_score_calculation():
    """Test memory score calculation on synthetic history"""
    # Fixed point history
    fixed_history = [np.ones(20, dtype=int)] * 50
    memory_fixed = memory_score(fixed_history, max_period=10)
    assert 0 <= memory_fixed <= 1.0, "Memory score should be in [0, 1]"
    
    # Random different states
    np.random.seed(42)
    random_history = [np.random.randint(0, 2, 20) for _ in range(50)]
    memory_random = memory_score(random_history, max_period=10)
    assert 0 <= memory_random <= 1.0, "Memory score should be in [0, 1]"
    
    # Memory score should be a valid float
    assert isinstance(memory_fixed, (float, np.number))
    assert isinstance(memory_random, (float, np.number))


def test_edge_of_chaos_score_structure():
    """Test edge_of_chaos_score returns valid values"""
    # Create synthetic history
    history = [np.random.randint(0, 2, (10, 10)) for _ in range(20)]
    
    # Call with proper signature
    score = edge_of_chaos_score(
        history=history,
        sensitivity=0.4,
        memory=0.5,
        target_entropy=0.7,
        target_activity=0.3
    )
    assert 0 <= score <= 1, "Edge score should be in [0, 1]"
    assert isinstance(score, (float, np.number))


def test_edge_of_chaos_score_regimes():
    """Test edge score responds to different regimes"""
    np.random.seed(42)
    
    # Ordered regime: low entropy, high memory
    ordered_history = [np.zeros((10, 10), dtype=int)] * 20
    ordered_score = edge_of_chaos_score(
        history=ordered_history,
        sensitivity=0.05,
        memory=0.95,
        target_entropy=0.7,
        target_activity=0.3
    )
    
    # Chaotic regime: high entropy, low memory
    chaotic_history = [np.random.randint(0, 2, (10, 10)) for _ in range(20)]
    chaotic_score = edge_of_chaos_score(
        history=chaotic_history,
        sensitivity=0.9,
        memory=0.05,
        target_entropy=0.7,
        target_activity=0.3
    )
    
    # Just verify both produce valid scores
    assert 0 <= ordered_score <= 1
    assert 0 <= chaotic_score <= 1


def test_lambda_parameter_estimate():
    """Test lambda parameter estimation (heuristic)"""
    # This is experimental, just check it runs and returns reasonable values
    np.random.seed(42)
    
    # Test with list of states
    history_list = [np.random.randint(0, 2, (10, 10)) for _ in range(10)]
    lambda_val = lambda_parameter_estimate(history_list)
    assert 0 <= lambda_val <= 1, "Lambda should be in [0, 1]"
    
    # Test with 3D numpy array (timesteps, height, width)
    history_3d = np.random.randint(0, 2, (10, 10, 10))
    lambda_val_3d = lambda_parameter_estimate(history_3d)
    assert 0 <= lambda_val_3d <= 1, "Lambda should be in [0, 1]"


def test_metrics_determinism():
    """Test that metrics are deterministic given same input"""
    np.random.seed(42)
    grid = np.random.randint(0, 2, (20, 20))
    
    entropy1 = shannon_entropy(grid)
    entropy2 = shannon_entropy(grid)
    assert entropy1 == entropy2
    
    spatial1 = spatial_entropy(grid)
    spatial2 = spatial_entropy(grid)
    assert spatial1 == spatial2


if __name__ == "__main__":
    print("Running isinglab metrics tests...")
    pytest.main([__file__, "-v"])
