"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from alforqan.backend.core.backgrounds.gradient_direction import ManimDirections

from .config import BackgroundStyle, PatternConfig
from .patterns import (
    DiagonalPoints,
    DiagonalSquare,
    DiagonalSquareDots,
    DiamondDots,
    GeometricStarsPattern,
    Grid,
    Hexagonal,
    StarMotifGeometricPattern,
)

from manim import *
from manim import Rectangle, Scene, VGroup
import structlog

logger = structlog.getLogger(__name__)


class BackgroundManager:
    """Manager class for background creation and handling."""

    def __init__(self):
        self.pattern_registry = {
            BackgroundStyle.STAR_MOTIF_GEOMETRIC: StarMotifGeometricPattern,
            BackgroundStyle.GEOMETRIC_STARS: GeometricStarsPattern,
            BackgroundStyle.GRID: Grid,
            BackgroundStyle.DIAGONAL_SQUARE: DiagonalSquare,
            BackgroundStyle.DIAGONAL_SQUARE_DOTS: DiagonalSquareDots,
            BackgroundStyle.DIAGONAL_POINTS: DiagonalPoints,
            BackgroundStyle.DIAMOND_DOTS: DiamondDots,
            BackgroundStyle.HEXAGONAL: Hexagonal,
        }

    def create_background(
        self,
        style: BackgroundStyle,
        color_scheme: list,
        gradient_direction: str,
        gradient_intensity: float,
        gradient: bool,
        pattern_config: PatternConfig,
    ) -> VGroup:
        """Create a complete background."""
        background = VGroup()

        gradient_intensity = max(0.0, min(1.0, gradient_intensity))  # Clamp between 0 and 1
        gradient_direction = ManimDirections().get_direction_vector(gradient_direction)
        logger.info(
            "Background settings",
            gradient=gradient,
            gradient_direction=gradient_direction,
            gradient_intensity=gradient_intensity,
            color_scheme=color_scheme,
            style=style,
        )

        # Create base background with gradient
        if gradient:
            # Use only the first color as base and let sheen create the gradient effect
            base = Rectangle(
                width=config.frame_width,
                height=config.frame_height,
                fill_color=color_scheme[0],  # Use first color as base
                fill_opacity=1,
                sheen_factor=gradient_intensity,  # This controls the gradient intensity
                sheen_direction=gradient_direction,
                stroke_width=0,
            )
        else:
            # Solid color without gradient
            base = Rectangle(
                width=config.frame_width,
                height=config.frame_height,
                fill_color=color_scheme[0],
                fill_opacity=1,
                stroke_width=0,
            )

        background.add(base)

        # For multi-color gradients, add additional layers with transparency
        if gradient and len(color_scheme) > 1:
            for i, color in enumerate(color_scheme[1:3], 1):  # Use up to 2 additional colors
                overlay = Rectangle(
                    width=config.frame_width,
                    height=config.frame_height,
                    fill_color=color,
                    fill_opacity=0.3 / i,  # Decreasing opacity for each layer
                    sheen_factor=gradient_intensity - 0.1,
                    sheen_direction=gradient_direction,
                    stroke_width=0,
                )
                background.add(overlay)

        # Add pattern if style is not basic
        if style not in [BackgroundStyle.SOLID, BackgroundStyle.GRADIENT]:
            if pattern_config is None:
                pattern_config = PatternConfig()

            pattern_class = self.pattern_registry.get(style)
            if pattern_class:
                pattern = pattern_class(color_scheme, pattern_config).create()
                background.add(pattern)

        return background


class BaseBackgroundScene(Scene):
    """Scene class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_manager = BackgroundManager()
        self.background_style: BackgroundStyle | None = None
        self.color_scheme: list | None = None
        self.gradient_direction: str | None = None
        self.gradient_intensity: float | None = None
        self.gradient: bool = True
        self.pattern_config: PatternConfig | None = None

    def initialize_background(
        self,
        background_style: BackgroundStyle,
        color_scheme: list,
        gradient_direction: str,
        gradient_intensity: float,
        gradient: bool,
        pattern_config: PatternConfig | None = None,
    ):
        """Initialize background."""
        self.background_style = background_style
        self.color_scheme = color_scheme
        self.gradient_direction = gradient_direction
        self.gradient_intensity = gradient_intensity
        self.gradient = gradient
        self.pattern_config = pattern_config or PatternConfig()

    def construct(self):
        """Create and add background to scene."""
        if self.background_style is None:
            raise ValueError("Background not initialized. Call initialize_background() first.")
        if self.color_scheme is None:
            raise ValueError("Color scheme not provided. Initialize with valid colors.")

        background = self.background_manager.create_background(
            style=self.background_style,
            color_scheme=self.color_scheme,
            gradient_direction=self.gradient_direction,
            gradient=self.gradient,
            pattern_config=self.pattern_config,
            gradient_intensity=self.gradient_intensity,
        )
        self.add(background)


# class BackgroundTestScene(Scene):
#     """Enhanced test scene to showcase all available background styles."""
#
#     def construct(self):
#         # Set up the scene with a light background
#         self.camera.background_color = "#FFFFFF"
#
#         # Create a styled title with adjusted position
#         title = Text("AlForqan Background Styles", font_size=40, color="#2C3E50").to_edge(UP, buff=0.3)
#         subtitle = Text("Available Pattern Options", font_size=24, color="#7F8C8D").next_to(title, DOWN, buff=0.15)
#
#         self.add(title, subtitle)
#
#         # Create a grid of samples with 4 columns
#         styles = list(BackgroundStyle)
#         rows = (len(styles) + 3) // 4  # Calculate rows needed for 4 columns
#         cols = 4
#
#         # Adjust sample size ratios for 4 columns
#         sample_width = config.frame_width / (cols + 1.2)  # Adjusted for 4 columns
#         sample_height = (config.frame_height - 2.5) / (rows + 1)  # Increased vertical spacing
#
#         samples = VGroup()
#         for i, style in enumerate(styles):
#             row = i // cols
#             col = i % cols
#
#             # Create a styled container with adjusted dimensions
#             container = Rectangle(
#                 width=sample_width * 0.8,  # Reduced width for 4 columns
#                 height=sample_height * 0.7,  # Adjusted height ratio
#                 stroke_width=1.5,  # Slightly thinner stroke
#                 stroke_color="#34495E",
#                 fill_opacity=0,
#             )
#
#             # Create and scale the background
#             sample_bg = BackgroundManager().create_background(
#                 style=style, color_scheme=COLOR_SCHEMES[ColorScheme.PRAYER_NIGHT], gradient_direction=UP, gradient=True
#             )
#             # Calculate scaling factors
#             width_scale = container.width * 0.85 / sample_bg.width
#             height_scale = container.height * 0.85 / sample_bg.height
#             scale_factor = min(width_scale, height_scale)
#             sample_bg.scale(scale_factor)
#
#             # Adjust positioning for 4 columns
#             x = (col - cols / 2 + 0.5) * (sample_width * 1.1)  # Adjusted horizontal spacing
#             y = (-row + rows / 2 - 0.5) * (sample_height * 1.2)  # Increased vertical spacing
#
#             # Ensure proper centering
#             container.move_to([x, y, 0])
#             sample_bg.move_to(container.get_center())
#
#             # Set proper z-index
#             sample_bg.set_z_index(-1)
#
#             # Create styled label with adjusted size
#             label = Text(
#                 style.value.replace("_", " ").title(),
#                 font_size=20,  # Slightly smaller font for 4 columns
#                 color="#2C3E50",
#             )
#             label.next_to(container, DOWN, buff=0.1)  # Reduced buffer
#
#             # Add refined shadow
#             shadow = container.copy()
#             shadow.set_stroke(width=0)
#             shadow.set_fill("#00000011", opacity=0.06)
#             shadow.shift(RIGHT * 0.03 + DOWN * 0.03)
#
#             # Group elements
#             sample_group = VGroup(shadow, container, sample_bg, label)
#             samples.add(sample_group)
#
#         # Shift entire samples group up slightly to balance vertical space
#         samples.shift(UP * 0.3)
#
#         self.add(samples)
