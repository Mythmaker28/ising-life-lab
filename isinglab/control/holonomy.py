"""
Contrôle Holonomique : Trajectoires dans l'espace des paramètres.

Concept : Au lieu de fixer des paramètres statiques, définir des "strokes"
(trajectoires fermées) dans l'espace de configuration. L'intégrale de la
phase géométrique le long de ces boucles produit la Phase de Berry.

Status actuel : SQUELETTE / INTERFACE
    - Structure de données pour définir les paths
    - Bibliothèque de strokes préfabriqués
    - L'implémentation complète de la Phase de Berry est TODO

Application phénoménologique :
    - Stroke "5meo_basic" : boucle simple → uniformisation
    - Stroke "dmt_chaos" : boucle complexe → fragmentation
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ParameterSpace(str, Enum):
    """Espaces de paramètres disponibles pour les trajectoires."""
    KERNEL_STRENGTHS = "kernel_strengths"  # (K1, K2, K3)
    KERNEL_RANGES = "kernel_ranges"  # (R1, R2, R3)
    FREQUENCY_LANDSCAPE = "frequency_landscape"  # ω(x,y)
    PROJECTION_MODULATION = "projection_modulation"  # Via ProjectionMap


@dataclass
class PathPoint:
    """Point dans une trajectoire paramétrique."""
    
    # Valeurs des paramètres à ce point
    params: Dict[str, float]
    
    # Temps relatif dans la trajectoire [0, 1]
    t: float
    
    # Optionnel : dérivée temporelle (pour calcul géométrique)
    d_params: Optional[Dict[str, float]] = None


class HolonomyPath:
    """
    Trajectoire dans l'espace des paramètres.
    
    Une boucle fermée (start = end) permet de calculer la Phase de Berry,
    qui caractérise la géométrie de l'espace des paramètres.
    
    Usage:
        # Définir un path simple
        path = HolonomyPath(space=ParameterSpace.KERNEL_STRENGTHS)
        path.add_point({"k1": 1.0, "k2": 0.0, "k3": 0.0}, t=0.0)
        path.add_point({"k1": 0.5, "k2": 0.5, "k3": 0.0}, t=0.5)
        path.add_point({"k1": 1.0, "k2": 0.0, "k3": 0.0}, t=1.0)
        
        # Interpoler pour obtenir un paramètre à t arbitraire
        params_mid = path.interpolate(t=0.25)
    """
    
    def __init__(
        self,
        space: ParameterSpace,
        name: str = "unnamed_path",
        description: str = ""
    ):
        """
        Args:
            space: Espace de paramètres où se déroule la trajectoire
            name: Nom descriptif du path
            description: Description longue (usage, effet attendu)
        """
        self.space = space
        self.name = name
        self.description = description
        self.points: List[PathPoint] = []
        
    def add_point(
        self,
        params: Dict[str, float],
        t: float,
        d_params: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Ajoute un point de contrôle à la trajectoire.
        
        Args:
            params: Valeurs des paramètres
            t: Temps normalisé [0, 1]
            d_params: Dérivées temporelles (optionnel)
        """
        point = PathPoint(params=params, t=t, d_params=d_params)
        self.points.append(point)
        
        # Trier par temps
        self.points.sort(key=lambda p: p.t)
        
    def interpolate(self, t: float) -> Dict[str, float]:
        """
        Interpolation linéaire entre les points de contrôle.
        
        Args:
            t: Temps normalisé [0, 1]
            
        Returns:
            Dictionnaire des paramètres interpolés
        """
        if not self.points:
            return {}
        
        # Wrap t dans [0, 1]
        t = t % 1.0
        
        # Trouver les deux points encadrants
        if t <= self.points[0].t:
            return self.points[0].params.copy()
        if t >= self.points[-1].t:
            return self.points[-1].params.copy()
        
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            if p1.t <= t <= p2.t:
                # Interpolation linéaire
                alpha = (t - p1.t) / (p2.t - p1.t + 1e-10)
                
                result = {}
                for key in p1.params:
                    v1 = p1.params[key]
                    v2 = p2.params.get(key, v1)
                    result[key] = v1 + alpha * (v2 - v1)
                
                return result
        
        return self.points[-1].params.copy()
    
    def is_closed_loop(self, tolerance: float = 1e-3) -> bool:
        """
        Vérifie si la trajectoire forme une boucle fermée.
        
        Args:
            tolerance: Tolérance pour la comparaison des paramètres
            
        Returns:
            True si start ≈ end
        """
        if len(self.points) < 2:
            return False
        
        p_start = self.points[0].params
        p_end = self.points[-1].params
        
        for key in p_start:
            if abs(p_start[key] - p_end.get(key, float('inf'))) > tolerance:
                return False
        
        return True
    
    def compute_geometric_phase(self) -> float:
        """
        Calcule la phase géométrique (Holonomie) de la trajectoire fermée.
        
        IMPLÉMENTATION P4 : Calcul basé sur l'aire orientée de la boucle
        dans l'espace des paramètres via le théorème de Green.
        
        Pour une boucle fermée dans l'espace (K1, K2) :
            Aire = (1/2) ∮ (K1 dK2 - K2 dK1)
        
        Cette aire est proportionnelle à la phase géométrique accumulée.
        
        Returns:
            Phase géométrique normalisée [0, 2π)
        """
        if not self.is_closed_loop(tolerance=0.1):
            raise ValueError("Le calcul de la phase géométrique requiert une boucle fermée.")
        
        if len(self.points) < 3:
            return 0.0
        
        # Extraire les paramètres K1, K2 de chaque point
        k1_values = []
        k2_values = []
        
        for point in self.points:
            k1_values.append(point.params.get('k1', 0.0))
            k2_values.append(point.params.get('k2', 0.0))
        
        # Calcul de l'aire via la formule du lacet (Shoelace formula)
        # Aire = (1/2) Σ (x_i * y_{i+1} - x_{i+1} * y_i)
        area = 0.0
        n = len(k1_values)
        
        for i in range(n):
            j = (i + 1) % n
            area += k1_values[i] * k2_values[j]
            area -= k1_values[j] * k2_values[i]
        
        area = abs(area) / 2.0
        
        # Normaliser à [0, 2π) : la phase géométrique est proportionnelle à l'aire
        # On utilise une normalisation arbitraire pour avoir une phase en radians
        phase = (area / (1.0 + area)) * 2 * np.pi
        
        return phase
    
    def compute_berry_phase(self) -> float:
        """
        Alias pour compute_geometric_phase() (compatibilité).
        
        Note : La Phase de Berry quantique complète nécessiterait les états |ψ>.
        Notre implémentation calcule la phase géométrique classique (Holonomie)
        dans l'espace des paramètres de contrôle.
        
        Returns:
            Phase géométrique γ ∈ [0, 2π)
        """
        return self.compute_geometric_phase()
    
    def to_dict(self) -> Dict:
        """Sérialise le path en dictionnaire (pour sauvegarde JSON)."""
        return {
            'space': self.space,
            'name': self.name,
            'description': self.description,
            'points': [
                {
                    'params': p.params,
                    't': p.t,
                    'd_params': p.d_params
                }
                for p in self.points
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HolonomyPath':
        """Désérialise depuis un dictionnaire."""
        path = cls(
            space=ParameterSpace(data['space']),
            name=data['name'],
            description=data['description']
        )
        
        for p_data in data['points']:
            path.add_point(
                params=p_data['params'],
                t=p_data['t'],
                d_params=p_data.get('d_params')
            )
        
        return path


def generate_linear_ramp_path(
    k_start: float,
    k_end: float,
    duration: float,
    n_steps: int = 10,
    annealing_start: float = 0.1,
    annealing_end: float = 0.5,
    name: str = "linear_ramp"
) -> HolonomyPath:
    """
    Génère une trajectoire linéaire simple K_start → K_end.
    
    Args:
        k_start: Force de couplage initiale
        k_end: Force de couplage finale
        duration: Durée totale normalisée [0, 1]
        n_steps: Nombre de points de contrôle
        annealing_start: Annealing initial
        annealing_end: Annealing final
        name: Nom de la trajectoire
        
    Returns:
        HolonomyPath paramétré
    """
    path = HolonomyPath(
        space=ParameterSpace.KERNEL_STRENGTHS,
        name=name,
        description=f"Linear ramp: K1={k_start:.2f}→{k_end:.2f}, annealing={annealing_start:.2f}→{annealing_end:.2f}"
    )
    
    for i in range(n_steps):
        t = i / (n_steps - 1) * duration
        alpha = i / (n_steps - 1)
        
        k1_current = k_start + alpha * (k_end - k_start)
        annealing_current = annealing_start + alpha * (annealing_end - annealing_start)
        
        path.add_point({
            "k1": k1_current,
            "k2": 0.0,
            "k3": 0.0,
            "annealing": annealing_current
        }, t=t)
    
    return path


def generate_smooth_sigmoid_path(
    k_start: float,
    k_end: float,
    duration: float,
    steepness: float = 5.0,
    n_steps: int = 15,
    annealing_profile: str = "increasing"
) -> HolonomyPath:
    """
    Génère une trajectoire sigmoïde (transition douce).
    
    Args:
        k_start: K1 initial
        k_end: K1 final
        duration: Durée normalisée
        steepness: Raideur de la sigmoïde (plus élevé = transition plus abrupte)
        n_steps: Nombre de points
        annealing_profile: 'increasing', 'decreasing', ou 'constant'
        
    Returns:
        HolonomyPath avec transition douce
    """
    path = HolonomyPath(
        space=ParameterSpace.KERNEL_STRENGTHS,
        name=f"sigmoid_{annealing_profile}",
        description=f"Smooth sigmoid: K={k_start:.2f}→{k_end:.2f}, profile={annealing_profile}"
    )
    
    def sigmoid(x, steepness):
        return 1 / (1 + np.exp(-steepness * (x - 0.5)))
    
    for i in range(n_steps):
        t = i / (n_steps - 1) * duration
        alpha = i / (n_steps - 1)
        
        # Transition sigmoïde pour K1
        sig_alpha = sigmoid(alpha, steepness)
        k1_current = k_start + sig_alpha * (k_end - k_start)
        
        # Profil d'annealing
        if annealing_profile == "increasing":
            annealing_current = 0.1 + 0.4 * alpha
        elif annealing_profile == "decreasing":
            annealing_current = 0.5 - 0.4 * alpha
        else:  # constant
            annealing_current = 0.3
        
        path.add_point({
            "k1": k1_current,
            "k2": 0.0,
            "k3": 0.0,
            "annealing": annealing_current
        }, t=t)
    
    return path


def generate_multi_stage_path(
    stages: List[Tuple[float, float, float]],
    duration: float = 1.0,
    n_steps_per_stage: int = 5
) -> HolonomyPath:
    """
    Génère une trajectoire multi-étapes.
    
    Args:
        stages: Liste de (k1, k2, annealing) pour chaque étape
        duration: Durée totale
        n_steps_per_stage: Points par étape
        
    Returns:
        HolonomyPath avec transitions multi-étapes
    """
    path = HolonomyPath(
        space=ParameterSpace.KERNEL_STRENGTHS,
        name="multi_stage",
        description=f"Multi-stage path with {len(stages)} stages"
    )
    
    n_stages = len(stages)
    stage_duration = duration / n_stages
    
    for stage_idx, (k1, k2, annealing) in enumerate(stages):
        for step_idx in range(n_steps_per_stage):
            t_global = (stage_idx + step_idx / n_steps_per_stage) * stage_duration
            
            path.add_point({
                "k1": k1,
                "k2": k2,
                "k3": 0.0,
                "annealing": annealing
            }, t=t_global)
    
    return path


def generate_closed_loop_path(
    k1_center: float,
    k2_center: float,
    radius_k1: float,
    radius_k2: float,
    n_points: int = 20,
    duration: float = 1.0,
    annealing: float = 0.3,
    phase_offset: float = 0.0,
    loop_type: str = "ellipse"
) -> HolonomyPath:
    """
    Génère une trajectoire fermée (boucle) dans l'espace (K1, K2).
    
    P4 IMPLEMENTATION : Trajectoires fermées pour accumuler une phase géométrique.
    
    Args:
        k1_center: Centre K1 de la boucle
        k2_center: Centre K2 de la boucle
        radius_k1: Rayon dans la direction K1
        radius_k2: Rayon dans la direction K2
        n_points: Nombre de points sur la boucle
        duration: Durée totale [0, 1]
        annealing: Valeur d'annealing (constante pour la boucle)
        phase_offset: Offset de phase initial [0, 2π]
        loop_type: 'ellipse' ou 'lissajous'
        
    Returns:
        HolonomyPath formant une boucle fermée
    """
    path = HolonomyPath(
        space=ParameterSpace.KERNEL_STRENGTHS,
        name=f"closed_loop_{loop_type}",
        description=f"Closed loop: center=({k1_center:.2f}, {k2_center:.2f}), radii=({radius_k1:.2f}, {radius_k2:.2f})"
    )
    
    for i in range(n_points + 1):  # +1 pour fermer la boucle
        t = i / n_points * duration
        theta = 2 * np.pi * i / n_points + phase_offset
        
        if loop_type == "ellipse":
            # Ellipse simple
            k1 = k1_center + radius_k1 * np.cos(theta)
            k2 = k2_center + radius_k2 * np.sin(theta)
            
        elif loop_type == "lissajous":
            # Courbe de Lissajous (plus complexe)
            k1 = k1_center + radius_k1 * np.cos(2 * theta)
            k2 = k2_center + radius_k2 * np.sin(3 * theta)
            
        else:  # circle
            k1 = k1_center + radius_k1 * np.cos(theta)
            k2 = k2_center + radius_k1 * np.sin(theta)  # Même rayon
        
        path.add_point({
            "k1": k1,
            "k2": k2,
            "k3": 0.0,
            "annealing": annealing
        }, t=t)
    
    return path


def generate_adaptive_loop_path(
    k1_start: float,
    k2_start: float,
    k1_amplitude: float,
    k2_amplitude: float,
    n_loops: int = 2,
    n_points_per_loop: int = 10,
    annealing_profile: str = "increasing"
) -> HolonomyPath:
    """
    Génère une trajectoire avec plusieurs boucles imbriquées.
    
    Utile pour explorer différentes amplitudes de phase géométrique.
    
    Args:
        k1_start: K1 initial
        k2_start: K2 initial
        k1_amplitude: Amplitude des oscillations K1
        k2_amplitude: Amplitude des oscillations K2
        n_loops: Nombre de boucles complètes
        n_points_per_loop: Points par boucle
        annealing_profile: 'increasing', 'decreasing', 'constant'
        
    Returns:
        HolonomyPath avec boucles multiples
    """
    path = HolonomyPath(
        space=ParameterSpace.KERNEL_STRENGTHS,
        name="adaptive_loop",
        description=f"Adaptive loop with {n_loops} cycles"
    )
    
    total_points = n_loops * n_points_per_loop
    
    for i in range(total_points + 1):
        t = i / total_points
        theta = 2 * np.pi * n_loops * t
        
        # Amplitude décroissante si requis
        amplitude_factor = 1.0 - 0.5 * t if annealing_profile == "decreasing" else 1.0
        
        k1 = k1_start + k1_amplitude * amplitude_factor * np.cos(theta)
        k2 = k2_start + k2_amplitude * amplitude_factor * np.sin(theta)
        
        # Profil d'annealing
        if annealing_profile == "increasing":
            annealing = 0.1 + 0.4 * t
        elif annealing_profile == "decreasing":
            annealing = 0.5 - 0.4 * t
        else:
            annealing = 0.3
        
        path.add_point({
            "k1": k1,
            "k2": k2,
            "k3": 0.0,
            "annealing": annealing
        }, t=t)
    
    return path


class StrokeLibrary:
    """
    Bibliothèque de strokes préfabriqués pour le contrôle holonomique.
    
    Chaque stroke est une trajectoire nommée avec un effet prévisible.
    MISE À JOUR : Maintenant avec générateurs paramétriques.
    """
    
    @staticmethod
    def make_5meo_basic(
        k_start: float = 1.5,
        k_end: float = 2.0,
        duration: float = 1.0,
        annealing_strength: float = 0.5
    ) -> HolonomyPath:
        """
        Stroke "5-MeO-DMT Basic" : Uniformisation progressive.
        
        PARAMÉTRABLE : Ajuste K_start, K_end, duration, annealing.
        
        Stratégie :
            1. K1 fort, K2/K3 nuls → synchronisation locale
            2. Annealing progressif → annihilation des défauts
            3. Convergence vers état uniforme (r → 1, #defects → 0)
        
        Args:
            k_start: K1 initial
            k_end: K1 final (généralement > k_start pour renforcer)
            duration: Durée de la trajectoire [0, 1]
            annealing_strength: Force de l'annealing final
            
        Returns:
            HolonomyPath paramétré
        """
        return generate_linear_ramp_path(
            k_start=k_start,
            k_end=k_end,
            duration=duration,
            n_steps=10,
            annealing_start=0.1,
            annealing_end=annealing_strength,
            name="5meo_basic_param"
        )
    
    @staticmethod
    def make_dmt_chaos(
        k1_strength: float = 1.0,
        k2_strength: float = 0.5,
        duration: float = 1.0,
        oscillation_frequency: float = 3.0
    ) -> HolonomyPath:
        """
        Stroke "DMT Chaos" : Fragmentation et instabilité.
        
        PARAMÉTRABLE : Ajuste forces de couplage et fréquence d'oscillation.
        
        Stratégie :
            1. Kernels compétitifs (K1 positif, K2 négatif)
            2. Oscillations de force → instabilité des défauts
            3. Haute densité de défauts persistants
        
        Args:
            k1_strength: Force du kernel K1
            k2_strength: Force du kernel K2 (sera négatif)
            duration: Durée de la trajectoire
            oscillation_frequency: Fréquence des oscillations
            
        Returns:
            HolonomyPath paramétré
        """
        path = HolonomyPath(
            space=ParameterSpace.KERNEL_STRENGTHS,
            name="dmt_chaos_param",
            description=f"Fragmentation chaotique : K1={k1_strength:.2f}, K2=-{k2_strength:.2f}, freq={oscillation_frequency:.1f}"
        )
        
        n_points = int(10 * oscillation_frequency)
        for i in range(n_points):
            t = i / (n_points - 1) * duration
            phase = 2 * np.pi * oscillation_frequency * t
            
            # Oscillations des kernels
            k1_osc = k1_strength * (1 + 0.2 * np.sin(phase))
            k2_osc = -k2_strength * (1 + 0.3 * np.cos(phase * 1.5))
            k3_osc = 0.2 * np.sin(phase * 0.5)
            
            path.add_point({
                "k1": k1_osc,
                "k2": k2_osc,
                "k3": k3_osc,
                "annealing": 0.05
            }, t=t)
        
        return path
    
    @staticmethod
    def make_salvia_geometry() -> HolonomyPath:
        """
        Stroke "Salvia Geometry" : Projection sphérique dynamique.
        
        Stratégie :
            1. Modulation spatiale via ProjectionMap
            2. Rotation du centre de projection
            3. Génération de patterns géométriques
        
        Returns:
            HolonomyPath fermé
        """
        path = HolonomyPath(
            space=ParameterSpace.PROJECTION_MODULATION,
            name="salvia_geometry",
            description="Modulation géométrique : rotation de l'axe de projection"
        )
        
        # Rotation sur la sphère
        angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
        
        for i, theta in enumerate(angles):
            # Point sur l'équateur
            x = np.cos(theta)
            y = np.sin(theta)
            z = 0.0
            
            path.add_point(
                {"center_x": x, "center_y": y, "center_z": z, "sigma": 0.5},
                t=i / 8.0
            )
        
        # Fermer la boucle
        path.add_point(
            {"center_x": 1.0, "center_y": 0.0, "center_z": 0.0, "sigma": 0.5},
            t=1.0
        )
        
        return path
    
    @staticmethod
    def list_all_strokes() -> List[str]:
        """Retourne la liste des noms de tous les strokes disponibles."""
        return [
            "5meo_basic",
            "dmt_chaos",
            "salvia_geometry"
        ]
    
    @classmethod
    def get_stroke(cls, name: str) -> HolonomyPath:
        """
        Récupère un stroke par son nom.
        
        Args:
            name: Nom du stroke
            
        Returns:
            HolonomyPath correspondant
            
        Raises:
            ValueError si le stroke n'existe pas
        """
        stroke_map = {
            "5meo_basic": cls.make_5meo_basic,
            "dmt_chaos": cls.make_dmt_chaos,
            "salvia_geometry": cls.make_salvia_geometry
        }
        
        if name not in stroke_map:
            raise ValueError(
                f"Stroke '{name}' inconnu. Disponibles : {list(stroke_map.keys())}"
            )
        
        return stroke_map[name]()

