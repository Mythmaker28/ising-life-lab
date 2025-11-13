"""
Projection Map : Synesthésie spatiale pour le contrôle des couplages.

Concept : Mapper un espace 3D virtuel (cube, sphère) sur la grille 2D
pour moduler spatialement les kernels de couplage.

Usage typique :
    - "Haut" de la sphère = cohérence maximale (K1 fort)
    - "Équateur" = zone de transition
    - Utilisé pour implémenter des "strokes" holonomiques
"""

import numpy as np
from typing import Tuple, Literal
from enum import Enum


class ProjectionType(str, Enum):
    """Type de projection 3D → 2D."""
    STEREOGRAPHIC = "stereographic"
    MERCATOR = "mercator"
    CUBE_FACE = "cube_face"
    RADIAL = "radial"


class ProjectionMap:
    """
    Mappe un espace virtuel 3D sur une grille 2D de simulation.
    
    Objectif : Créer des modulations spatiales des paramètres de couplage
    basées sur une géométrie 3D intuitive.
    
    Usage:
        pmap = ProjectionMap(grid_shape=(256, 256), projection='stereographic')
        distance_field = pmap.compute_distance_to_point([0, 0, 1])  # Pôle nord
        
        # Utiliser distance_field pour moduler K1 :
        # K1_modulated = K1_base * exp(-distance_field / sigma)
    """
    
    def __init__(
        self,
        grid_shape: Tuple[int, int],
        projection: ProjectionType = ProjectionType.STEREOGRAPHIC,
        radius: float = 1.0
    ):
        """
        Args:
            grid_shape: (H, W) de la grille 2D
            projection: Type de projection
            radius: Rayon de la sphère virtuelle
        """
        self.grid_shape = grid_shape
        self.projection = projection
        self.radius = radius
        
        # Précompute les coordonnées 3D pour chaque point de la grille
        self._coords_3d = self._compute_3d_coordinates()
        
    def _compute_3d_coordinates(self) -> np.ndarray:
        """
        Calcule les coordonnées 3D pour chaque pixel de la grille 2D.
        
        Returns:
            Array de shape (H, W, 3) contenant (x, y, z)
        """
        h, w = self.grid_shape
        coords = np.zeros((h, w, 3), dtype=np.float32)
        
        if self.projection == ProjectionType.STEREOGRAPHIC:
            # Projection stéréographique : grille 2D → sphère
            # Formule : x = 2u/(1+u²+v²), y = 2v/(1+u²+v²), z = (1-u²-v²)/(1+u²+v²)
            
            # Normaliser la grille [0, H-1] × [0, W-1] → [-2, 2] × [-2, 2]
            u = np.linspace(-2, 2, w)
            v = np.linspace(-2, 2, h)
            uu, vv = np.meshgrid(u, v)
            
            denom = 1 + uu**2 + vv**2
            coords[:, :, 0] = 2 * uu / denom * self.radius
            coords[:, :, 1] = 2 * vv / denom * self.radius
            coords[:, :, 2] = (1 - uu**2 - vv**2) / denom * self.radius
            
        elif self.projection == ProjectionType.MERCATOR:
            # Projection de Mercator : longitude/latitude
            lon = np.linspace(0, 2 * np.pi, w)
            lat = np.linspace(-np.pi/2, np.pi/2, h)
            lon_grid, lat_grid = np.meshgrid(lon, lat)
            
            coords[:, :, 0] = self.radius * np.cos(lat_grid) * np.cos(lon_grid)
            coords[:, :, 1] = self.radius * np.cos(lat_grid) * np.sin(lon_grid)
            coords[:, :, 2] = self.radius * np.sin(lat_grid)
            
        elif self.projection == ProjectionType.RADIAL:
            # Projection radiale simple : disque 2D → dôme hémisphérique
            x = np.linspace(-1, 1, w)
            y = np.linspace(-1, 1, h)
            xx, yy = np.meshgrid(x, y)
            
            r_sq = xx**2 + yy**2
            z = np.sqrt(np.maximum(0, 1 - r_sq))
            
            coords[:, :, 0] = xx * self.radius
            coords[:, :, 1] = yy * self.radius
            coords[:, :, 2] = z * self.radius
            
        else:  # CUBE_FACE
            # Face du cube (z = 1)
            x = np.linspace(-1, 1, w)
            y = np.linspace(-1, 1, h)
            xx, yy = np.meshgrid(x, y)
            
            coords[:, :, 0] = xx * self.radius
            coords[:, :, 1] = yy * self.radius
            coords[:, :, 2] = np.ones((h, w)) * self.radius
        
        return coords
    
    def compute_distance_to_point(
        self,
        point_3d: Tuple[float, float, float]
    ) -> np.ndarray:
        """
        Calcule la distance euclidienne entre chaque pixel et un point 3D.
        
        Args:
            point_3d: (x, y, z) dans l'espace 3D virtuel
            
        Returns:
            Champ 2D de distances
        """
        px, py, pz = point_3d
        
        dx = self._coords_3d[:, :, 0] - px
        dy = self._coords_3d[:, :, 1] - py
        dz = self._coords_3d[:, :, 2] - pz
        
        distance = np.sqrt(dx**2 + dy**2 + dz**2)
        
        return distance
    
    def compute_geodesic_distance(
        self,
        point_3d: Tuple[float, float, float]
    ) -> np.ndarray:
        """
        Calcule la distance géodésique (sur la sphère) au lieu d'euclidienne.
        
        Utile pour des modulations plus "naturelles" sur la sphère.
        
        Args:
            point_3d: (x, y, z) sur la sphère (normalisé à radius)
            
        Returns:
            Champ 2D de distances géodésiques (en radians)
        """
        px, py, pz = point_3d
        
        # Normaliser le point cible
        p_norm = np.sqrt(px**2 + py**2 + pz**2)
        if p_norm < 1e-6:
            return np.zeros(self.grid_shape, dtype=np.float32)
        
        px, py, pz = px / p_norm, py / p_norm, pz / p_norm
        
        # Normaliser les coordonnées de la grille
        coords_norm = self._coords_3d.copy()
        norms = np.sqrt(np.sum(coords_norm**2, axis=2, keepdims=True))
        norms[norms < 1e-6] = 1.0
        coords_norm /= norms
        
        # Produit scalaire → angle
        dot_product = (
            coords_norm[:, :, 0] * px +
            coords_norm[:, :, 1] * py +
            coords_norm[:, :, 2] * pz
        )
        dot_product = np.clip(dot_product, -1.0, 1.0)
        
        geodesic_distance = np.arccos(dot_product)
        
        return geodesic_distance * self.radius
    
    def create_gaussian_modulation(
        self,
        center_3d: Tuple[float, float, float],
        sigma: float,
        use_geodesic: bool = True
    ) -> np.ndarray:
        """
        Crée un champ de modulation gaussien centré sur un point 3D.
        
        Usage typique : moduler K1 autour d'une "région active".
        
        Args:
            center_3d: Centre du spot gaussien
            sigma: Largeur de la gaussienne
            use_geodesic: Si True, utilise la distance géodésique
            
        Returns:
            Champ 2D multiplicatif exp(-d²/2σ²)
        """
        if use_geodesic:
            distance = self.compute_geodesic_distance(center_3d)
        else:
            distance = self.compute_distance_to_point(center_3d)
        
        modulation = np.exp(-distance**2 / (2 * sigma**2))
        
        return modulation
    
    def get_3d_coordinates(self) -> np.ndarray:
        """
        Retourne les coordonnées 3D précomputées.
        
        Returns:
            Array (H, W, 3)
        """
        return self._coords_3d.copy()
    
    def visualize_projection(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Retourne les champs X, Y, Z pour visualisation.
        
        Returns:
            (x_field, y_field, z_field) chacun de shape (H, W)
        """
        return (
            self._coords_3d[:, :, 0],
            self._coords_3d[:, :, 1],
            self._coords_3d[:, :, 2]
        )

