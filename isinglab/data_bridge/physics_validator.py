"""
Validateur physique : Vérifie si des paramètres phénoménologiques
sont réalisables sous des contraintes quantiques réelles.
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

from .atlas_map import AtlasProfile, PhenoParams


@dataclass
class ValidationResult:
    """Résultat de validation physique."""
    
    is_valid: bool
    score: float  # [0, 1]
    violations: list
    warnings: list
    
    def __repr__(self):
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        return f"ValidationResult({status}, score={self.score:.2f}, violations={len(self.violations)})"


class PhysicsValidator:
    """
    Validateur de contraintes physiques.
    
    Vérifie que les paramètres phénoménologiques proposés respectent
    les limites imposées par la physique quantique du système.
    """
    
    # Seuils de validité
    MIN_T2_FOR_COHERENT_OPS = 1.0  # µs
    MIN_T1_T2_RATIO = 2.0
    MAX_NOISE_FOR_CONTROL = 0.3
    MAX_K_T2_PRODUCT = 100.0  # K·T2 < threshold (couplage vs décohérence)
    
    def __init__(self, strict: bool = False):
        """
        Args:
            strict: Si True, applique des critères plus restrictifs
        """
        self.strict = strict
    
    def validate(
        self,
        pheno_params: PhenoParams,
        atlas_profile: AtlasProfile
    ) -> ValidationResult:
        """
        Valide si les paramètres phéno sont réalisables physiquement.
        
        Args:
            pheno_params: Paramètres phénoménologiques proposés
            atlas_profile: Profil physique du système
            
        Returns:
            ValidationResult avec score et violations
        """
        violations = []
        warnings = []
        score = 1.0
        
        # Test 1 : T2 minimal pour opérations cohérentes
        if atlas_profile.t2_us < self.MIN_T2_FOR_COHERENT_OPS:
            violations.append(
                f"T2={atlas_profile.t2_us:.2f}µs < {self.MIN_T2_FOR_COHERENT_OPS}µs (trop court pour cohérence)"
            )
            score *= 0.3
        
        # Test 2 : Ratio T1/T2 raisonnable
        ratio = atlas_profile.t1_us / (atlas_profile.t2_us + 1e-6)
        if ratio < self.MIN_T1_T2_RATIO:
            warnings.append(
                f"T1/T2={ratio:.1f} < {self.MIN_T1_T2_RATIO} (T1 devrait être > T2)"
            )
            score *= 0.8
        
        # Test 3 : Bruit compatible avec le contrôle
        if pheno_params.noise_amplitude > self.MAX_NOISE_FOR_CONTROL:
            if self.strict:
                violations.append(
                    f"Noise={pheno_params.noise_amplitude:.3f} > {self.MAX_NOISE_FOR_CONTROL} (trop bruité)"
                )
                score *= 0.4
            else:
                warnings.append(
                    f"Noise={pheno_params.noise_amplitude:.3f} élevé, contrôle difficile"
                )
                score *= 0.7
        
        # Test 4 : Couplage K1 vs temps de cohérence
        k_t2_product = pheno_params.k1_strength * atlas_profile.t2_us
        if k_t2_product > self.MAX_K_T2_PRODUCT:
            warnings.append(
                f"K1·T2={k_t2_product:.1f} > {self.MAX_K_T2_PRODUCT} (couplage fort vs courte cohérence)"
            )
            score *= 0.9
        
        # Test 5 : Annealing compatible avec la température
        expected_annealing = self._expected_annealing(atlas_profile.temperature_k)
        annealing_error = abs(pheno_params.annealing_rate - expected_annealing) / (expected_annealing + 1e-6)
        if annealing_error > 0.5:
            warnings.append(
                f"Annealing={pheno_params.annealing_rate:.3f} vs attendu={expected_annealing:.3f} (écart {annealing_error*100:.0f}%)"
            )
            score *= 0.95
        
        # Test 6 : Fréquence vs pas de temps
        min_dt = 1.0 / (100.0 * atlas_profile.frequency_ghz)
        if pheno_params.dt < min_dt:
            warnings.append(
                f"dt={pheno_params.dt:.4f} très petit pour f={atlas_profile.frequency_ghz:.2f}GHz"
            )
            score *= 0.95
        
        is_valid = len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            violations=violations,
            warnings=warnings
        )
    
    def _expected_annealing(self, temperature_k: float) -> float:
        """Calcule l'annealing attendu pour une température donnée."""
        return 0.5 * np.exp(-(temperature_k / 300.0))
    
    def batch_validate(
        self,
        pheno_params_list: list,
        atlas_profile: AtlasProfile
    ) -> list:
        """Valide un batch de paramètres."""
        return [self.validate(p, atlas_profile) for p in pheno_params_list]
    
    def filter_valid(
        self,
        pheno_params_list: list,
        atlas_profile: AtlasProfile,
        min_score: float = 0.6
    ) -> list:
        """
        Filtre les paramètres valides avec score > threshold.
        
        Returns:
            Liste de tuples (params, validation_result)
        """
        results = self.batch_validate(pheno_params_list, atlas_profile)
        
        valid = []
        for params, result in zip(pheno_params_list, results):
            if result.is_valid and result.score >= min_score:
                valid.append((params, result))
        
        return valid

