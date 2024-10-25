"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BackgroundStyle(Enum):
    """Enumeration of available background styles."""

    SOLID = "solid"
    GRADIENT = "gradient"
    STAR_MOTIF_GEOMETRIC = "star_motif_geometric"
    GEOMETRIC_STARS = "geometric_stars"

    GRID = "grid"
    DIAGONAL_SQUARE = "diagonal_square"
    DIAGONAL_SQUARE_DOTS = "diagonal_square_dots"
    DIAGONAL_POINTS = "diagonal_points"
    DIAMOND_DOTS = "diamond_dots"
    HEXAGONAL = "hexagonal"


@dataclass
class PatternConfig:
    """Configuration class for pattern generation with smart defaults."""

    scale: float = 1.0
    opacity: float = 0.7
    stroke: float = 1.0
    spacing: float = 0.5
    point_radius: float = 0.03
    density: int = 20  # Controls pattern density (number of elements)

    def __post_init__(self):
        from manim import config

        # Calculate viewport dimensions
        self.width = config.frame_width
        self.height = config.frame_height
        self.aspect_ratio = self.width / self.height
        # Grid dimensions based on viewport and scale
        self.cols = int(self.width / (self.scale * 2)) + 2
        self.rows = int(self.height / (self.scale * 2)) + 2
        # Pattern-specific calculations
        self.element_size = self.scale * self.spacing
        self.grid_range = range(-self.density, self.density + 1)
