"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from alforqan.backend.core.backgrounds.config import PatternConfig

from manim import VGroup, VMobject
import numpy as np

T = TypeVar("T", bound=VMobject)


class BasePattern(ABC):
    """Base class for all pattern implementations with common utilities."""

    def __init__(self, color_scheme: list[str], pattern_config: PatternConfig):
        self.colors = color_scheme
        self.config = pattern_config
        self._pattern: VGroup | None = None

    @abstractmethod
    def create(self) -> VGroup:
        """Create the pattern. Must be implemented by subclasses."""
        pass

    def _create_grid_elements(self, element_factory: type[T], **kwargs) -> VGroup:
        """Utility method for creating grid-based patterns."""
        pattern = VGroup()
        for i in self.config.grid_range:
            for j in self.config.grid_range:
                pos = np.array([i * self.config.element_size, j * self.config.element_size, 0])
                element = element_factory(**kwargs)
                element.move_to(pos)
                pattern.add(element)
        return pattern

    def apply_style(self, pattern: VGroup, fill: bool = False) -> VGroup:
        """Apply common styling to pattern."""
        if fill:
            pattern.set_fill(color=self.colors[0], opacity=self.config.opacity)
        pattern.set_stroke(color=self.colors[1], width=self.config.stroke, opacity=self.config.opacity)
        return pattern
