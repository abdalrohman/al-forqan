"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from ..config import PatternConfig
from .base_patterns import BasePattern

from manim import PI, RIGHT, UP, Line, Polygon, VGroup
import numpy as np


class GeometricStarsPattern(BasePattern):
    """Implementation of the geometric stars pattern."""

    def __init__(self, color_scheme: list[str], pattern_config: PatternConfig):
        super().__init__(color_scheme, pattern_config)
        # Pattern-specific configurations
        self.star_points = 8
        self.base_size = 0.8 * self.config.scale
        self.spacing = self.base_size * 2
        self.outer_radius_ratio = 0.5
        self.inner_radius_ratio = 0.3
        self.inner_star_scale = 0.4  # Scale factor for inner star details

    def create(self) -> VGroup:
        """Create the complete geometric stars pattern."""
        pattern = VGroup()

        # Create the pattern grid
        for i in range(-self.config.cols, self.config.cols + 1):
            for j in range(-self.config.rows, self.config.rows + 1):
                # Create and position star
                star = self._create_star()
                star.move_to(np.array([i * self.spacing, j * self.spacing, 0]))
                pattern.add(star)

                # Add connections
                if i < self.config.cols:
                    pattern.add(self._create_connection(star, direction="horizontal"))
                if j < self.config.rows:
                    pattern.add(self._create_connection(star, direction="vertical"))

        # Apply styling
        return self.apply_style(pattern)

    def _create_star(self) -> VGroup:
        """Create an individual geometric star with inner details."""
        star = VGroup()

        # Calculate radii
        outer_radius = self.base_size * self.outer_radius_ratio
        inner_radius = self.base_size * self.inner_radius_ratio

        # Create main star
        star.add(
            Polygon(*self._generate_star_points(outer_radius=outer_radius, inner_radius=inner_radius), stroke_width=self.config.stroke * 2)
        )

        # Create inner star detail
        inner_outer_radius = outer_radius * self.inner_star_scale
        inner_inner_radius = inner_radius * self.inner_star_scale
        star.add(
            Polygon(
                *self._generate_star_points(outer_radius=inner_outer_radius, inner_radius=inner_inner_radius),
                stroke_width=self.config.stroke,
            )
        )

        return star

    def _generate_star_points(self, outer_radius: float, inner_radius: float) -> list[np.ndarray]:
        """Generate points for a star polygon with improved precision."""
        points: list[np.ndarray] = []

        for i in range(2 * self.star_points):
            # Calculate angle and radius for each point
            angle = i * PI / self.star_points
            radius = outer_radius if i % 2 == 0 else inner_radius

            # Generate point coordinates
            point = np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
            points.append(point)

        return points

    def _create_connection(self, star: VGroup, direction: str) -> VGroup:
        """Create connecting pattern between stars with improved positioning."""
        connection = VGroup()

        # Calculate connection positions based on direction
        if direction == "horizontal":
            start_point = star.get_right()
            end_point = start_point + RIGHT * (self.spacing - star.get_width())
        else:  # vertical
            start_point = star.get_top()
            end_point = start_point + UP * (self.spacing - star.get_height())

        # Create connection line with proper styling
        connection.add(Line(start=start_point, end=end_point, stroke_width=self.config.stroke))

        return connection

    def apply_style(self, pattern: VGroup, fill: bool = False) -> VGroup:  # noqa: ARG002
        """Apply custom styling to the pattern."""
        pattern.set_stroke(color=self.colors[1], opacity=self.config.opacity)
        return pattern
