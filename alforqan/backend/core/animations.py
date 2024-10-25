"""
Description: This module provides custom animation functionalities for the Manim library,
specifically designed to be used for the AlForqan project.

Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)

License: MIT

Requirements:
    - manim
    - numpy
"""

from __future__ import annotations

__all__ = ["create_high_performance_animations"]


from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import math
from typing import Any

from manim import Animation, Text, VGroup, config
from manim.utils import rate_functions
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class FrameOptimizedAnimation(Animation):
    """
    Highly optimized animation class with frame skipping
    """

    def __init__(
        self,
        mobject: Text,
        mode: str = "write",
        batch_size: int = 8,
        time_width: float = 0.5,
        frame_skip: int = 2,  # Only render every nth frame
        rtl: bool = True,  # Right-to-left direction for languages like Arabic
        **kwargs,
    ):
        self.mode = mode
        self.time_width = time_width
        self.frame_skip = frame_skip
        self.rtl = rtl
        self.total_chars = len(mobject.original_text) + 10  # Add 10 letter extra to ensure all text disappear when unwriting
        self.batch_size = min(batch_size, self.total_chars)

        # Batch calculations
        self.num_batches = math.ceil(self.total_chars / self.batch_size)

        logger.debug("Total Chars: ", total_cahrs=self.total_chars)
        logger.debug("Batch size: ", batch_size=self.batch_size)
        logger.debug("Number of batches: ", num_batches=self.num_batches)

        # Create batches based on direction
        if rtl:
            # For RTL, reverse the batch order
            self.batches = [
                slice(
                    max(self.total_chars - (i + 1) * batch_size, 0),
                    self.total_chars - i * batch_size,
                )
                for i in range(self.num_batches)
            ]
        else:
            # LTR batch order
            self.batches = [
                slice(
                    i * batch_size,
                    min((i + 1) * batch_size, self.total_chars),
                )
                for i in range(self.num_batches)
            ]

        logger.debug("Batches: ", batches=self.batches)

        # Pre-compute animation parameters
        self.batch_starts = np.linspace(0, 1 - time_width, self.num_batches)
        if mode == "unwrite":
            self.batch_starts = 1 - self.batch_starts - time_width

        # Initialize cache
        self._opacity_cache = {}
        self._last_alpha = None
        self._last_opacities = np.zeros(self.total_chars)

        super().__init__(mobject, **kwargs)

    @lru_cache(maxsize=128)  # noqa: B019
    def _calculate_batch_opacity(self, batch_idx: int, alpha: float) -> np.ndarray[Any, np.dtype[np.floating[Any]]]:
        """Cached calculation of batch opacity values."""
        time = alpha
        batch_time = (time - self.batch_starts[batch_idx]) / self.time_width
        opacity = np.clip(a=batch_time, a_min=-0.001, a_max=1)
        return 1 - opacity if self.mode == "unwrite" else opacity

    def interpolate_mobject(self, alpha):
        # Skip frames for performance
        if self._last_alpha is not None and abs(alpha - self._last_alpha) < (1.0 / (config.frame_rate / self.frame_skip)):
            return

        self._last_alpha = alpha

        # Update opacities in batches
        for batch_idx, batch_slice in enumerate(self.batches):
            opacity = self._calculate_batch_opacity(batch_idx, alpha)
            self._last_opacities[batch_slice] = opacity

        # Bulk update mobject opacities
        for i, opacity in enumerate(self._last_opacities):
            if i < len(self.mobject):
                self.mobject[i].set_opacity(opacity)


def create_high_performance_animations(
    verse_group: VGroup,
    duration: float,
    batch_size: int = 8,
    frame_skip: int = 2,
    rtl: bool = True,
) -> tuple[list[Animation], Animation, list[Animation], float]:
    """
    Creates highly optimized animations with parallel processing support.
    """

    def create_single_animation(text, mode, run_time):
        return FrameOptimizedAnimation(
            text,
            mode=mode,
            batch_size=batch_size,
            frame_skip=frame_skip,
            run_time=run_time,
            rate_func=rate_functions.ease_in_out_cubic if mode == "write" else rate_functions.ease_in_out_expo,
            rtl=rtl,
        )

    # Calculate timings
    total_chars = sum(len(text.original_text) for text in verse_group)
    write_time = min(duration * 0.35, total_chars * 0.04)
    scale_time = min(duration * 0.1, 0.3)

    # Create animations in parallel
    with ThreadPoolExecutor() as executor:
        write_futures = [
            executor.submit(
                create_single_animation,
                text,
                "write",
                write_time,
            )
            for text in verse_group
        ]
        unwrite_futures = [
            executor.submit(
                create_single_animation,
                text,
                "unwrite",
                write_time,
            )
            for text in verse_group
        ]

        write_anims = [f.result() for f in write_futures]
        unwrite_anims = [f.result() for f in unwrite_futures]

    # Create scale animation
    scale_anim = verse_group.animate(rate_func=rate_functions.ease_in_sine).scale(1.2)

    return write_anims, scale_anim, unwrite_anims, scale_time
