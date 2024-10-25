"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from .base_patterns import BasePattern

from manim import RegularPolygon, VGroup
import numpy as np


class Hexagonal(BasePattern):
    """Optimized hexagonal pattern."""

    def create(self) -> VGroup:
        pattern = VGroup()
        hex_size = self.config.element_size

        for i in self.config.grid_range:
            for j in self.config.grid_range:
                hex = RegularPolygon(n=6, start_angle=0)
                hex.set(height=hex_size)
                hex.move_to(np.array([i * hex_size * np.sqrt(3), j * hex_size * 1.5 + (i % 2) * hex_size * 0.75, 0]))
                pattern.add(hex)

        return self.apply_style(pattern)
