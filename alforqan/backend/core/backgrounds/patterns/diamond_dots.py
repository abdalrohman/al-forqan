"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from .base_patterns import BasePattern

from manim import PI, Dot, Square, VGroup
import numpy as np


class DiamondDots(BasePattern):
    """Diamond dots pattern."""

    def create(self) -> VGroup:
        pattern = VGroup()
        diamond_size = 0.5 * self.config.scale

        for i in self.config.grid_range:
            for j in self.config.grid_range:
                # Create diamond (rotated square)
                diamond = Square(side_length=diamond_size)
                diamond.rotate(PI / 4)
                diamond.move_to(np.array([i * diamond_size, j * diamond_size, 0]))
                pattern.add(diamond)

                # Add centered dot
                dot = Dot(point=diamond.get_center(), radius=self.config.point_radius)
                pattern.add(dot)

        # Apply styling
        pattern.set_stroke(color=self.colors[1], width=self.config.stroke, opacity=self.config.opacity - 0.2)
        pattern.set_fill(color=self.colors[0], opacity=self.config.opacity)
        return pattern


# class DiamondDots(BasePattern):
#     def create(self) -> VGroup:
#         """Create a diamond pattern with dots."""
#         pattern = VGroup()
#         diamond_size = 0.5
#         for i in range(-20, 21):
#             for j in range(-20, 21):
#                 # Create a diamond shape using a rotated square
#                 diamond = Square(side_length=diamond_size)
#                 diamond.rotate(PI / 4)  # Rotate 45 degrees
#                 # Position diamonds in a grid: (i*size, j*size)
#                 diamond.move_to(np.array([i * diamond_size, j * diamond_size, 0]))
#                 pattern.add(diamond)
#                 dot = Dot(point=diamond.get_center(), radius=0.03)
#                 pattern.add(dot)
#         pattern.set_stroke(color=self.colors[1], width=self.config.stroke, opacity=self.config.opacity - 0.2)
#         pattern.set_fill(color=self.colors[0], opacity=self.config.opacity)
#         return pattern
