"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from .base_patterns import BasePattern

from manim import PI, Line, Polygon, VGroup
import numpy as np


class StarMotifGeometricPattern(BasePattern):
    """
    Implementation of an Islamic-inspired geometric pattern featuring intricate star motifs
    arranged in a repeating grid. The pattern consists of 8-pointed stars with connecting
    geometric elements forming a continuous interlaced design.
    """

    def create(self) -> VGroup:
        """
        Creates the complete pattern by arranging pattern units in a grid.
        Returns a VGroup containing all pattern elements.
        """
        pattern = VGroup()
        unit_size = 1.0 * self.config.scale

        # Create pattern grid by repeating the basic unit
        for i in range(-self.config.cols, self.config.cols + 1):
            for j in range(-self.config.rows, self.config.rows + 1):
                # Create and position each unit
                unit = self._create_pattern_unit(unit_size)
                unit.move_to(np.array([i * unit_size, j * unit_size, 0]))
                pattern.add(unit)

        # Adjust stroke properties for better visibility
        pattern.set_stroke(width=1.0)  # Increased stroke width for more prominence
        pattern.set_stroke(color=self.colors[1], opacity=0.85)  # Slightly adjusted opacity
        return pattern

    def _create_pattern_unit(self, size: float) -> VGroup:
        """
        Creates a single unit of the pattern containing the star and connecting elements.
        """
        unit = VGroup()

        # Layer 1: Create the primary star structure
        primary_star = self._create_eight_pointed_star(size * 0.85)  # Increased size for better overlap
        unit.add(primary_star)

        # Layer 2: Add internal geometric details
        inner_details = self._create_inner_details(size * 0.65)
        unit.add(inner_details)

        # Layer 3: Add connecting elements between stars
        connectors = self._create_connectors(size)
        unit.add(connectors)

        # Layer 4: Add decorative details
        decorative_elements = self._create_additional_details(size * 0.55)
        unit.add(decorative_elements)

        return unit

    def _create_eight_pointed_star(self, size: float) -> VGroup:
        """
        Creates an eight-pointed star with intricate internal structure.
        """
        star = VGroup()

        # Create the main star points with enhanced geometry
        for i in range(8):
            angle1 = i * PI / 4
            angle2 = (i + 1) * PI / 4
            angle3 = (i + 2) * PI / 4

            # Calculate star point coordinates
            point1 = size * np.array([np.cos(angle1), np.sin(angle1), 0])
            point2 = size * 0.45 * np.array([np.cos(angle2), np.sin(angle2), 0])  # Adjusted inner point
            point3 = size * np.array([np.cos(angle3), np.sin(angle3), 0])

            # Create star point shape
            triangle = Polygon(point1, point2, point3)
            star.add(triangle)

            # Add detailed internal lines
            for j in range(2):
                midpoint = (point1 + point3) / 2
                detail_line = Line(point2, midpoint)
                star.add(detail_line)

        return star

    def _create_inner_details(self, size: float) -> VGroup:
        """
        Creates the intricate geometric details inside the star.
        """
        details = VGroup()

        # Create octagonal inner frame
        octagon_points = [size * np.array([np.cos(i * PI / 4), np.sin(i * PI / 4), 0]) for i in range(8)]

        # Add octagon edges
        for i in range(8):
            line = Line(octagon_points[i], octagon_points[(i + 1) % 8])
            details.add(line)

        # Add crossing lines for additional detail
        for i in range(4):
            angle = i * PI / 2
            point1 = size * np.array([np.cos(angle), np.sin(angle), 0])
            point2 = size * np.array([np.cos(angle + PI), np.sin(angle + PI), 0])
            details.add(Line(point1, point2))

        return details

    def _create_connectors(self, size: float) -> VGroup:
        """
        Creates the connecting elements between pattern units.
        """
        connectors = VGroup()

        # Create diagonal connectors at corners
        for i in range(4):
            angle = i * PI / 2 + PI / 4

            # Calculate connector points
            point1 = size * np.array([np.cos(angle), np.sin(angle), 0])
            point2 = size * 0.75 * np.array([np.cos(angle + PI / 8), np.sin(angle + PI / 8), 0])
            point3 = size * 0.75 * np.array([np.cos(angle - PI / 8), np.sin(angle - PI / 8), 0])

            # Create connector shape
            connector = Polygon(point1, point2, point3)
            connectors.add(connector)

            # Add reinforcing lines
            connectors.add(Line(point1, point2), Line(point1, point3))

        return connectors

    def _create_additional_details(self, size: float) -> VGroup:
        """
        Creates additional decorative details to enhance pattern complexity.
        """
        details = VGroup()

        # Add small geometric shapes at intersection points
        for i in range(8):
            angle = i * PI / 4
            center = size * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])

            # Create small diamond at each intersection
            diamond_points = []
            diamond_size = size * 0.12  # Adjusted size for better proportion

            for j in range(4):
                diamond_angle = j * PI / 2 + PI / 4
                point = center + diamond_size * np.array([np.cos(diamond_angle), np.sin(diamond_angle), 0])
                diamond_points.append(point)

            diamond = Polygon(*diamond_points)
            details.add(diamond)

        return details
