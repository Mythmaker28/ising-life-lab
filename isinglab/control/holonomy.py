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
    
    def compute_berry_phase(self) -> float:
        """
        Calcule la Phase de Berry le long de la trajectoire fermée.
        
        TODO: Implémentation complète nécessite :
            1. État quantique |ψ(t)> pour chaque point
            2. Intégrale de la connexion de Berry : γ = i ∮ <ψ|∂_t ψ> dt
            3. Projection sur les états propres du système
        
        Pour l'instant : PLACEHOLDER retournant 0.
        
        Returns:
            Phase géométrique γ ∈ [0, 2π)
        """
        if not self.is_closed_loop():
            raise ValueError("Le calcul de la Phase de Berry requiert une boucle fermée.")
        
        # TODO: Implémentation réelle
        return 0.0
    
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


class StrokeLibrary:
    """
    Bibliothèque de strokes préfabriqués pour le contrôle holonomique.
    
    Chaque stroke est une trajectoire nommée avec un effet prévisible.
    """
    
    @staticmethod
    def make_5meo_basic() -> HolonomyPath:
        """
        Stroke "5-MeO-DMT Basic" : Uniformisation progressive.
        
        Stratégie :
            1. K1 fort, K2/K3 nuls → synchronisation locale
            2. Annealing progressif → annihilation des défauts
            3. Convergence vers état uniforme (r → 1, #defects → 0)
        
        Returns:
            HolonomyPath fermé
        """
        path = HolonomyPath(
            space=ParameterSpace.KERNEL_STRENGTHS,
            name="5meo_basic",
            description="Uniformisation progressive : K1 dominant avec annealing"
        )
        
        # Phase 1 : K1 fort
        path.add_point({"k1": 1.5, "k2": 0.0, "k3": 0.0, "annealing": 0.1}, t=0.0)
        
        # Phase 2 : Maintien avec réduction du bruit
        path.add_point({"k1": 1.5, "k2": 0.0, "k3": 0.0, "annealing": 0.5}, t=0.5)
        
        # Phase 3 : Retour (boucle fermée)
        path.add_point({"k1": 1.5, "k2": 0.0, "k3": 0.0, "annealing": 0.1}, t=1.0)
        
        return path
    
    @staticmethod
    def make_dmt_chaos() -> HolonomyPath:
        """
        Stroke "DMT Chaos" : Fragmentation et instabilité.
        
        Stratégie :
            1. Kernels compétitifs (K1 positif, K2 négatif)
            2. Oscillations de force → instabilité des défauts
            3. Haute densité de défauts persistants
        
        Returns:
            HolonomyPath fermé
        """
        path = HolonomyPath(
            space=ParameterSpace.KERNEL_STRENGTHS,
            name="dmt_chaos",
            description="Fragmentation chaotique : kernels compétitifs multi-échelle"
        )
        
        # Phase 1 : K1 positif, K2 négatif
        path.add_point({"k1": 1.0, "k2": -0.5, "k3": 0.2}, t=0.0)
        
        # Phase 2 : Inversion partielle
        path.add_point({"k1": 0.5, "k2": -1.0, "k3": 0.5}, t=0.33)
        
        # Phase 3 : Oscillation
        path.add_point({"k1": 1.2, "k2": -0.3, "k3": -0.2}, t=0.66)
        
        # Phase 4 : Retour (boucle fermée)
        path.add_point({"k1": 1.0, "k2": -0.5, "k3": 0.2}, t=1.0)
        
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

