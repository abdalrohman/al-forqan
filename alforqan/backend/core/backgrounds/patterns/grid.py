"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from .base_patterns import BasePattern

from manim import Line, VGroup
import numpy as np


class Grid(BasePattern):
    """Optimized grid pattern."""

    def create(self) -> VGroup:
        pattern = VGroup()

        # Horizontal lines
        for x in np.arange(-self.config.width / 2, self.config.width / 2, self.config.spacing):
            pattern.add(Line(start=np.array([x, -self.config.height / 2, 0]), end=np.array([x, self.config.height / 2, 0])))

        # Vertical lines
        for y in np.arange(-self.config.height / 2, self.config.height / 2, self.config.spacing):
            pattern.add(Line(start=np.array([-self.config.width / 2, y, 0]), end=np.array([self.config.width / 2, y, 0])))

        return self.apply_style(pattern)
