"""
Tests unitaires pour Reservoir Computing v4.0.
"""

import pytest
import numpy as np
from isinglab.brain_modules import get_brain_rule_function
from isinglab.reservoir import (
    CAReservoir,
    generate_narma10,
    generate_mackey_glass,
    generate_denoising_data,
    evaluate_narma,
    evaluate_mackey_glass,
    evaluate_denoising
)
from isinglab.reservoir.baselines import SimpleESN, SimpleMLP, LinearBaseline


def test_ca_reservoir_basic():
    """Test création et fonctionnement basique de CAReservoir."""
    rule_func = get_brain_rule_function('life')
    reservoir = CAReservoir(
        rule_function=rule_func,
        grid_size=(16, 16),
        steps=10
    )
    
    # Test encode
    input_data = np.random.rand(16, 16)
    initial_state = reservoir.encode_input(input_data)
    assert initial_state.shape == (16, 16)
    assert initial_state.dtype == int
    
    # Test evolve
    history = reservoir.evolve(initial_state, steps=5)
    assert len(history) == 6  # initial + 5 steps
    assert all(state.shape == (16, 16) for state in history)
    
    # Test extract_features
    features = reservoir.extract_features(history)
    assert len(features) > 0
    assert isinstance(features, np.ndarray)


def test_ca_reservoir_train_predict():
    """Test entraînement et prédiction CAReservoir."""
    rule_func = get_brain_rule_function('life')
    reservoir = CAReservoir(
        rule_function=rule_func,
        grid_size=(16, 16),
        steps=10
    )
    
    # Générer données d'entraînement simples
    n_samples = 20
    X_features = []
    y_target = []
    
    for i in range(n_samples):
        input_data = np.random.rand(16, 16)
        initial_state = reservoir.encode_input(input_data)
        history = reservoir.evolve(initial_state, steps=10)  # Utiliser même steps que reservoir
        features = reservoir.extract_features(history)
        X_features.append(features)
        y_target.append(np.random.rand())
    
    X_features = np.array(X_features)
    y_target = np.array(y_target)
    
    # Entraîner
    reservoir.train_readout(X_features, y_target)
    assert reservoir.is_trained
    
    # Prédire
    test_input = np.random.rand(16, 16)
    prediction = reservoir.predict(test_input)
    assert len(prediction) > 0


def test_generate_narma10():
    """Test génération données NARMA10."""
    u, y = generate_narma10(n_samples=100, seed=42)
    assert len(u) == 100
    assert len(y) == 100
    assert u.min() >= 0
    assert u.max() <= 0.5


def test_generate_mackey_glass():
    """Test génération données Mackey-Glass."""
    y = generate_mackey_glass(n_samples=100, seed=42)
    assert len(y) == 100
    assert y.min() >= 0


def test_generate_denoising_data():
    """Test génération données débruitage."""
    X_noisy, y_clean = generate_denoising_data(n_samples=10, grid_size=(16, 16), seed=42)
    assert len(X_noisy) == 10
    assert len(y_clean) == 10
    assert X_noisy[0].shape == (16, 16)
    assert y_clean[0].shape == (16, 16)


def test_baseline_esn():
    """Test baseline ESN."""
    esn = SimpleESN(reservoir_size=50, seed=42)
    
    # Données simples
    X = np.random.rand(20, 10)
    y = np.random.rand(20)
    
    esn.train(X, y)
    assert esn.is_trained
    
    predictions = esn.predict(X[:5])
    assert len(predictions) == 5


def test_baseline_mlp():
    """Test baseline MLP."""
    mlp = SimpleMLP(hidden_size=20, random_state=42)
    
    X = np.random.rand(20, 10)
    y = np.random.rand(20)
    
    mlp.train(X, y)
    assert mlp.is_trained
    
    predictions = mlp.predict(X[:5])
    assert len(predictions) == 5


def test_baseline_linear():
    """Test baseline linéaire."""
    linear = LinearBaseline(alpha=1.0)
    
    X = np.random.rand(20, 10)
    y = np.random.rand(20)
    
    linear.train(X, y)
    assert linear.is_trained
    
    predictions = linear.predict(X[:5])
    assert len(predictions) == 5


def test_evaluate_narma():
    """Test évaluation NARMA."""
    rule_func = get_brain_rule_function('life')
    reservoir = CAReservoir(
        rule_function=rule_func,
        grid_size=(16, 16),
        steps=10,
        input_encoder='temporal'
    )
    
    u, y = generate_narma10(n_samples=200, seed=42)
    results = evaluate_narma(reservoir, u, y, train_ratio=0.7)
    
    assert 'nmse' in results
    assert 'mse' in results
    assert results['nmse'] >= 0


def test_evaluate_denoising():
    """Test évaluation débruitage."""
    rule_func = get_brain_rule_function('life')
    reservoir = CAReservoir(
        rule_function=rule_func,
        grid_size=(16, 16),
        steps=10
    )
    
    X_noisy, y_clean = generate_denoising_data(n_samples=30, grid_size=(16, 16), seed=42)
    results = evaluate_denoising(reservoir, X_noisy, y_clean, train_ratio=0.7)
    
    assert 'accuracy' in results
    assert 'mse' in results
    assert 0 <= results['accuracy'] <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


