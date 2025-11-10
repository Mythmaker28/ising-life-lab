"""
Tests for isinglab public API (evaluate_rule, evaluate_batch, quick_scan)
"""
import pytest
import numpy as np
from isinglab.api import evaluate_rule, evaluate_batch, quick_scan


def test_evaluate_rule_basic():
    """Test basic evaluate_rule call for Rule 30 (chaotic)"""
    result = evaluate_rule(
        rule=30,
        ca_type="elementary",
        grid_size=50,
        steps=50,
        seed=42
    )
    
    # Check structure - metrics are flat in result dict
    assert isinstance(result, dict)
    assert "rule" in result
    assert "grid_size" in result
    assert "steps" in result
    
    # Check metrics presence (flat, not nested)
    required_metrics = [
        "entropy", "spatial_entropy", 
        "sensitivity", "memory_score", "edge_score",
        "activity", "attractor_type", "lambda_estimate"
    ]
    for metric in required_metrics:
        assert metric in result, f"Missing metric: {metric}"
        if metric != "attractor_type":
            assert isinstance(result[metric], (int, float, np.number))
    
    # Rule 30 is chaotic: expect high entropy, low memory
    assert result["entropy"] > 0.5, "Rule 30 should have high entropy"
    assert result["activity"] > 0.3, "Rule 30 should be active"
    assert result["memory_score"] < 0.5, "Rule 30 should have low memory"


def test_evaluate_rule_deterministic():
    """Test that same seed produces identical results"""
    result1 = evaluate_rule(rule=110, ca_type="elementary", grid_size=40, steps=40, seed=123)
    result2 = evaluate_rule(rule=110, ca_type="elementary", grid_size=40, steps=40, seed=123)
    
    # Compare all numeric metrics
    numeric_keys = ["entropy", "spatial_entropy", "sensitivity", "memory_score", 
                    "edge_score", "activity", "lambda_estimate"]
    for key in numeric_keys:
        assert abs(result1[key] - result2[key]) < 1e-9, \
            f"Metric {key} not deterministic"


def test_evaluate_rule_different_seeds():
    """Test that different seeds produce different results"""
    result1 = evaluate_rule(rule=90, ca_type="elementary", grid_size=30, steps=30, seed=1)
    result2 = evaluate_rule(rule=90, ca_type="elementary", grid_size=30, steps=30, seed=999)
    
    # At least one metric should differ (due to random IC)
    numeric_keys = ["entropy", "spatial_entropy", "sensitivity", "activity"]
    diffs = [abs(result1[k] - result2[k]) for k in numeric_keys]
    assert any(d > 1e-6 for d in diffs), "Different seeds should produce different results"


def test_evaluate_batch():
    """Test batch evaluation of multiple rules"""
    rules = [0, 30, 110, 184]  # trivial, chaotic, complex, identity
    results = evaluate_batch(
        rules=rules,
        ca_type="elementary",
        grid_size=30,
        steps=30,
        n_seeds=2,
        seed=42
    )
    
    assert len(results) == len(rules)
    
    # Check Rule 0 (trivial dead)
    rule0 = next(r for r in results if r["rule"] == 0)
    assert rule0["activity"] < 0.1, "Rule 0 should be inactive"
    
    # Check Rule 30 (chaotic)
    rule30 = next(r for r in results if r["rule"] == 30)
    assert rule30["entropy"] > 0.5, "Rule 30 should be chaotic"


def test_quick_scan():
    """Test quick_scan helper function"""
    results = quick_scan(
        rule_range=(0, 15),
        ca_type="elementary",
        grid_size=20,
        steps=20,
        seed=42
    )
    
    assert len(results) == 16  # 0 to 15 inclusive
    assert all("rule" in r for r in results)
    assert all("edge_score" in r for r in results)


def test_evaluate_rule_ising():
    """Test that Ising model evaluation works"""
    result = evaluate_rule(
        rule={"T": 2.5, "J": 1.0, "h": 0.0},  # Ising params as dict
        grid_size=20,
        steps=50,
        seed=42
    )
    
    assert result["rule"]["T"] == 2.5
    assert "entropy" in result
    assert result["entropy"] > 0


def test_evaluate_rule_invalid_ca_type():
    """Test that invalid CA type raises appropriate error"""
    with pytest.raises(ValueError, match="Unknown CA type"):
        evaluate_rule(
            rule=30,
            ca_type="invalid_type",
            grid_size=20,
            steps=20,
            seed=42
        )


if __name__ == "__main__":
    print("Running isinglab API tests...")
    pytest.main([__file__, "-v"])

