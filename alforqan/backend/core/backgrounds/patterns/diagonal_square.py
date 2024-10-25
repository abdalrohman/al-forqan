"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from .base_patterns import BasePattern

from manim import PI, Dot, Square, VGroup
import numpy as np


class DiagonalSquare(BasePattern):
    """Diagonal square pattern."""

    def create(self) -> VGroup:
        pattern = VGroup()
        square_size = 0.5 * self.config.scale

        for i in self.config.grid_range:
            for j in self.config.grid_range:
                square = Square(side_length=square_size)
                square.move_to(np.array([i * square_size, j * square_size, 0]))
                square.rotate(PI / 4)
                pattern.add(square)

        pattern.set_stroke(color=self.colors[1], width=self.config.stroke, opacity=self.config.opacity)
        return pattern


class DiagonalSquareDots(DiagonalSquare):
    """Diagonal square dots pattern."""

    def create(self) -> VGroup:
        # Get the base diagonal square pattern
        pattern = super().create()
        dots = VGroup()

        # Add centered dots to each square
        for square in pattern:
            dot = Dot(point=square.get_center(), radius=self.config.point_radius)
            dots.add(dot)

        # Apply styling to dots
        dots.set_fill(color=self.colors[1], opacity=self.config.opacity)
        pattern.add(dots)
        return pattern


# class DiagonalSquare(BasePattern):
#     def create(self) -> VGroup:
#         """Create a diagonal square pattern."""
#         pattern = VGroup()
#         square_size = 0.5
#         # Create a grid of squares rotated 45 degrees
#         for i in range(-20, 21):
#             for j in range(-20, 21):
#                 square = Square(side_length=square_size)
#                 # Position squares in a grid: (i*size, j*size)
#                 square.move_to(np.array([i * square_size, j * square_size, 0]))
#                 square.rotate(PI / 4)  # Rotate 45 degrees
#                 pattern.add(square)
#         pattern.set_stroke(color=self.colors[1], width=self.config.stroke, opacity=self.config.opacity)
#         return pattern
#
#
# class DiagonalSquareDots(DiagonalSquare):
#     def create(self) -> VGroup:
#         pattern = super().create()
#         dots = VGroup()
#         for square in pattern:
#             dot = Dot(point=square.get_center(), radius=0.03)
#             dots.add(dot)
#         dots.set_fill(color=self.colors[1], opacity=self.config.opacity)
#         pattern.add(dots)
#         return pattern
