"""
Ising/CA Regime Profiles (Heuristic Analogies, NOT Predictions)

Suggests target CA/Ising parameter profiles based on physical system properties.

⚠️ CRITICAL DISCLAIMER:
- These are CONCEPTUAL ANALOGIES, not physical predictions
- We do NOT predict T₂, quantum behavior, or actual system dynamics
- Purpose: Explore which CA/Ising regimes might share QUALITATIVE features
  with different classes of physical systems
- All mappings are HEURISTIC and EXPERIMENTAL

Example use case:
    "Systems with long coherence might benefit from exploring CA rules
     with stable attractors + moderate sensitivity (memory-like regimes)"
"""

from typing import Dict, List, Optional
import numpy as np


# ============================================================================
# TARGET PROFILE DEFINITIONS
# ============================================================================

def get_target_profile_for_system(
    modality: str,
    temperature_regime: str,
    coherence_class: str
) -> Dict:
    """
    Suggest a target CA/Ising exploration profile (HEURISTIC).
    
    This function returns suggested ranges for:
        - edge_score: Target edge-of-chaos score
        - memory_score: Target memory-like behavior
        - sensitivity: Target Hamming sensitivity
        - entropy: Target entropy range
        - activity: Target activity level
    
    ⚠️ These are SUGGESTIONS for exploration, NOT predictions.
    
    Args:
        modality: System modality (optical, spin, nuclear, etc.)
        temperature_regime: Temperature category
        coherence_class: Coherence time category
        
    Returns:
        Dictionary with target ranges and rationale
    """
    profile = {
        "modality": modality,
        "temperature_regime": temperature_regime,
        "coherence_class": coherence_class,
        "suggested_regimes": [],
        "target_metrics": {},
        "rationale": "",
        "confidence": "low"  # Always low - this is heuristic
    }
    
    # ========================================================================
    # COHERENCE-BASED HEURISTICS
    # ========================================================================
    
    if coherence_class == "long" or coherence_class == "record":
        # Long coherence → Explore memory-like, stable regimes
        profile["target_metrics"] = {
            "edge_score": (0.4, 0.7),      # Edge-of-chaos to ordered
            "memory_score": (0.6, 1.0),    # High memory
            "sensitivity": (0.1, 0.5),     # Moderate to low sensitivity
            "entropy": (0.3, 0.6),         # Moderate entropy
            "activity": (0.2, 0.5)         # Moderate activity
        }
        profile["suggested_regimes"] = ["stable_attractors", "limit_cycles", "edge_of_chaos"]
        profile["rationale"] = (
            "Long coherence systems maintain information over time. "
            "Analogous CA/Ising regimes: stable attractors, limit cycles, memory-like behavior."
        )
    
    elif coherence_class == "short":
        # Short coherence → Explore chaotic, high-entropy regimes
        profile["target_metrics"] = {
            "edge_score": (0.3, 0.6),      # Chaotic to edge
            "memory_score": (0.0, 0.3),    # Low memory
            "sensitivity": (0.6, 1.0),     # High sensitivity
            "entropy": (0.7, 1.0),         # High entropy
            "activity": (0.5, 0.9)         # High activity
        }
        profile["suggested_regimes"] = ["chaotic", "high_entropy", "mixing"]
        profile["rationale"] = (
            "Short coherence systems lose information rapidly. "
            "Analogous CA/Ising regimes: chaotic dynamics, high entropy, mixing behavior."
        )
    
    elif coherence_class == "medium":
        # Medium coherence → Explore edge-of-chaos
        profile["target_metrics"] = {
            "edge_score": (0.5, 0.8),      # Edge-of-chaos
            "memory_score": (0.3, 0.7),    # Moderate memory
            "sensitivity": (0.3, 0.7),     # Moderate sensitivity
            "entropy": (0.4, 0.7),         # Moderate entropy
            "activity": (0.3, 0.6)         # Moderate activity
        }
        profile["suggested_regimes"] = ["edge_of_chaos", "complex", "adaptive"]
        profile["rationale"] = (
            "Medium coherence systems balance stability and dynamics. "
            "Analogous CA/Ising regimes: edge-of-chaos, complex behavior, critical transitions."
        )
    
    # ========================================================================
    # TEMPERATURE-BASED ADJUSTMENTS (Heuristic)
    # ========================================================================
    
    if temperature_regime == "cryogenic":
        # Cryogenic → Favor ordered regimes (less thermal noise)
        if "target_metrics" in profile and profile["target_metrics"]:
            # Shift towards more ordered behavior
            profile["target_metrics"]["entropy"] = tuple(
                max(0, e - 0.1) for e in profile["target_metrics"]["entropy"]
            )
            profile["rationale"] += " Cryogenic temps → explore more ordered regimes."
    
    elif temperature_regime == "high":
        # High temp → Favor chaotic regimes (more thermal noise)
        if "target_metrics" in profile and profile["target_metrics"]:
            profile["target_metrics"]["entropy"] = tuple(
                min(1, e + 0.1) for e in profile["target_metrics"]["entropy"]
            )
            profile["rationale"] += " High temps → explore more chaotic regimes."
    
    # ========================================================================
    # MODALITY-SPECIFIC NOTES (Informational only)
    # ========================================================================
    
    if modality == "optical":
        profile["notes"] = "Optical systems: typically fast dynamics, potential for entanglement."
    elif modality == "spin":
        profile["notes"] = "Spin systems: dipolar interactions, spin-spin coupling."
    elif modality == "nuclear":
        profile["notes"] = "Nuclear systems: long coherence, weak coupling."
    elif modality == "radical_pair":
        profile["notes"] = "Radical pairs: spin-dependent chemistry, potential magnetic field effects."
    else:
        profile["notes"] = "Unknown modality: broad exploration recommended."
    
    # Default fallback if no coherence class
    if not profile["target_metrics"]:
        profile["target_metrics"] = {
            "edge_score": (0.3, 0.8),
            "memory_score": (0.2, 0.8),
            "sensitivity": (0.2, 0.8),
            "entropy": (0.3, 0.8),
            "activity": (0.2, 0.7)
        }
        profile["suggested_regimes"] = ["broad_exploration"]
        profile["rationale"] = "Insufficient data → broad exploration recommended."
    
    return profile


def suggest_ca_rules_for_profile(profile: Dict, n_suggestions: int = 10) -> List[int]:
    """
    Suggest CA rules to explore based on target profile (HEURISTIC).
    
    ⚠️ This is a PLACEHOLDER heuristic. In practice, you would:
        1. Pre-compute metrics for all 256 elementary rules
        2. Filter by target metric ranges
        3. Return top matches
    
    For now, returns random suggestions based on regime hints.
    
    Args:
        profile: Target profile dict (from get_target_profile_for_system)
        n_suggestions: Number of rules to suggest
        
    Returns:
        List of suggested rule numbers
    """
    regimes = profile.get("suggested_regimes", [])
    
    # Heuristic rule suggestions (based on known CA behaviors)
    if "chaotic" in regimes:
        # Known chaotic rules
        candidates = [30, 45, 86, 89, 105, 122, 126, 129, 135, 149, 169]
    elif "stable_attractors" in regimes or "limit_cycles" in regimes:
        # Known stable/cyclic rules
        candidates = [2, 4, 8, 16, 20, 32, 34, 40, 50, 56, 58, 62, 72, 74, 76, 78]
    elif "edge_of_chaos" in regimes:
        # Known complex/edge rules
        candidates = [110, 124, 137, 142, 150, 152, 154, 156, 170, 178, 180, 182]
    else:
        # Broad exploration
        candidates = list(range(1, 255))
    
    # Random sample (deterministic with seed if provided)
    np.random.seed(42)
    suggestions = np.random.choice(
        candidates,
        size=min(n_suggestions, len(candidates)),
        replace=False
    ).tolist()
    
    return suggestions


def generate_search_config(profile: Dict, output_path: Optional[str] = None) -> Dict:
    """
    Generate a YAML-compatible search config from a profile.
    
    This config can be used with isinglab.scan_rules or evolutionary search.
    
    Args:
        profile: Target profile dict
        output_path: If provided, save to YAML file
        
    Returns:
        Config dictionary
    """
    config = {
        "description": f"Search config for {profile['modality']} / {profile['coherence_class']}",
        "rationale": profile.get("rationale", ""),
        
        "scan_params": {
            "ca_type": "elementary",
            "grid_size": 100,
            "steps": 200,
            "seeds_per_rule": 3,
            "random_seed": 42
        },
        
        "filter_criteria": {
            "edge_score": profile["target_metrics"].get("edge_score", (0.0, 1.0)),
            "memory_score": profile["target_metrics"].get("memory_score", (0.0, 1.0)),
            "sensitivity": profile["target_metrics"].get("sensitivity", (0.0, 1.0)),
            "entropy": profile["target_metrics"].get("entropy", (0.0, 1.0)),
            "activity": profile["target_metrics"].get("activity", (0.0, 1.0))
        },
        
        "output": {
            "results_csv": f"outputs/regime_search_{profile['modality']}_{profile['coherence_class']}.csv",
            "top_rules_json": f"outputs/top_rules_{profile['modality']}_{profile['coherence_class']}.json"
        }
    }
    
    if output_path:
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    return config

