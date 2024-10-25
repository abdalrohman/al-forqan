"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from ..config import PatternConfig
from .base_patterns import BasePattern

from manim import PI, Dot, VGroup


class DiagonalPoints(BasePattern):
    """Diagonal points pattern."""

    def create(self) -> VGroup:
        self.config = PatternConfig(
            spacing=0.3,
            density=31,
        )
        pattern = self._create_grid_elements(Dot, radius=self.config.point_radius)
        pattern.set_fill(color=self.colors[1], opacity=self.config.opacity)
        pattern.rotate(PI / 4)
        return pattern
