"""
Description: This module provides a framework for generating animated visualizations of Quranic verses using
the Manim animation engine. It creates high-quality videos and images featuring Arabic text with customizable styling,
backgrounds, and animations.
Usage:
    scene = QuranVerseScene(
        verses=["بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ"],
        verse_info="Al-Fātiḥah",
        durations=[5.0],
        font_path="path/to/font.ttf"
    )
    scene.render()
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
Requirements:
    - manim
    - pygame
"""

from __future__ import annotations

__all__ = ["QuranVerseScene"]

from datetime import datetime
from functools import lru_cache
from pathlib import Path
import textwrap

from alforqan.backend.core.animations import create_high_performance_animations
from alforqan.backend.core.backgrounds import BackgroundStyle, BaseBackgroundScene
from alforqan.backend.core.color_scheme import COLOR_SCHEMES, ColorScheme
from alforqan.backend.utils.font_helper import FontHelper

from manim import *
import pygame
import structlog

# Configure logging
logger = structlog.getLogger(__name__)


class QuranVerseScene(BaseBackgroundScene):
    """
    A customizable Manim scene for displaying Quran verses with additional information.

    This class provides a flexible framework for creating animations of Quran verses
    with various customization options including background styles, color schemes,
    and font settings.

    :param verses: A list of verse texts to display.
    :param verse_info: Information about the verse to display at the bottom.
    :param durations: A list of durations for each verse.
    :param font_path: Path to the font file for verse text.
    :param font_size: Size of the font for the verse text. Default is 36.
    :param info_font_size: Size of the font for the verse information. Default is 24.
    :param font_path_info: Path to the font file for verse information. Default is None.
    :param audio_paths: List of paths to audio files. Default is None.
    :param mode: Output mode, either "video" or "image". Default is "video".
    :param quality: Quality setting for the output. Default is "high_quality".
    :param aspect_ratio: Aspect ratio of the output. Default is "16:9".
    """

    def __init__(
        self,
        verses: list[str],
        verse_info: str,
        durations: list[float],
        font_path: str,
        **kwargs,
    ):
        # Store style information before calling super().__init__()
        self._background_style = kwargs.get("background_style", BackgroundStyle.STAR_MOTIF_GEOMETRIC)
        self._color_scheme = kwargs.get("color_scheme", ColorScheme.PRAYER_NIGHT)
        self._gradient = kwargs.get("gradient", True)
        self._gradient_direction = kwargs.get("gradient_direction", UP)

        # Initialize default values
        self.verses = verses
        self.verse_info = verse_info
        self.durations = durations
        self.font_path = font_path
        self.font_path_info = kwargs.get("font_path_info") or self.font_path
        self.font_size = kwargs.get("font_size", 36)
        self.info_font_size = kwargs.get("info_font_size", 24)
        self.audio_paths = kwargs.get("audio_paths", "")
        self.aspect_ratio = kwargs.get("aspect_ratio", "16:9")  # 16:9, 9:16, 12:12
        self.mode = kwargs.get("mode", "video")  # image, video
        self.quality = kwargs.get("quality", "high_quality")
        self.output_dir = kwargs.get("output_dir")
        self.output_file = kwargs.get("output_file")

        self._validate_inputs()
        self._configure_output()
        self._set_manim_config()
        self._print_screen_info()

        super().__init__()

        # Initialize background
        self.initialize_background(
            background_style=self._background_style,
            color_scheme=COLOR_SCHEMES[self._color_scheme],
            gradient_direction=self._gradient_direction,
            gradient=self._gradient,
        )

    def _validate_inputs(self):
        """Validate input parameters."""
        if len(self.verses) != len(self.durations):
            raise ValueError(f"Number of verses ({len(self.verses)}) must match number of durations ({len(self.durations)}).")

        if self.mode.lower() not in ["image", "video"]:
            raise ValueError(f"Mode must be 'image' or 'video', not '{self.mode}'.")

        if self.mode.lower() == "image" and len(self.verses) > 1:
            raise ValueError("Image mode only supports a single verse. Use video mode for multiple verses.")

        if self.quality not in constants.QUALITIES:
            raise KeyError(f"Quality must be one of {list(constants.QUALITIES.keys())}")

    def _configure_output(self):
        """Configure output settings based on aspect ratio and quality."""
        frame_width, frame_height = map(int, self.aspect_ratio.split(":"))
        config.frame_width = frame_width
        config.frame_height = frame_height

        config_quality = constants.QUALITIES[self.quality]
        if frame_width > frame_height:  # Widescreen
            config.frame_size = config_quality["pixel_width"], config_quality["pixel_height"]
            config.frame_rate = 24
            self.screen_type = "widescreen"
        elif frame_width < frame_height:  # Vertical
            config.frame_size = config_quality["pixel_height"], config_quality["pixel_width"]
            self.screen_type = "vertical"
            config.frame_rate = 24
        else:  # Square
            config.frame_width = config.frame_height = min(config_quality["pixel_width"], config_quality["pixel_height"])
            self.screen_type = "square"
            config.frame_rate = 24

    def _set_manim_config(self):
        """Set Manim configuration based on output mode."""
        config.flush_cache = False
        config.verbosity = "INFO"
        config.renderer = "cairo"
        config.disable_caching = True  # disable caching to speed up the rendering time
        config.disable_caching_warning = True
        config.media_dir = self.output_dir if self.output_dir is not None else config.media_dir

        if self.mode.lower() == "image":
            config.save_last_frame = True
            config.write_to_movie = False
            config.format = "png"
            config.images_dir = Path(config.media_dir) / "images_dir"
            config.output_file = self.output_file if self.output_file is not None else f"{self.__class__.__name__}.png"
        else:
            config.save_last_frame = False
            config.write_to_movie = True
            config.format = "mp4"
            config.video_dir = Path(config.media_dir) / "video_dir"
            config.output_file = (
                self.output_file if self.output_file is not None else f"{self.__class__.__name__}{config.movie_file_extension}"
            )

    def _print_screen_info(self):
        """Print detailed formatted information about the scene's configuration."""
        info_sections = {
            "Scene Configuration": [
                ("Scene Name", self.__class__.__name__),
                ("Creation Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),  # noqa: DTZ005
                ("Output Mode", self.mode.upper()),
                ("Quality Setting", self.quality),
            ],
            "Display Settings": [
                ("Aspect Ratio", f"{self.aspect_ratio} ({self.screen_type})"),
                ("Frame Dimensions", f"{config.frame_width:.2f} x {config.frame_height:.2f}"),
                ("Pixel Dimensions", f"{config.pixel_width} x {config.pixel_height}"),
                ("Frame Rate", f"{config.frame_rate} fps"),
            ],
            "Content Details": [
                ("Number of Verses", len(self.verses)),
                ("Total Duration", f"{sum(self.durations):.2f}s"),
                ("Font Size (Verse)", self.font_size),
                ("Font Size (Info)", self.info_font_size),
            ],
            "Style Information": [
                ("Background Style", self._background_style.value),
                ("Color Scheme", self._color_scheme.value),
                ("Gradient Enabled", "Yes" if self._gradient else "No"),
                ("Gradient Direction", str(self._gradient_direction)),
            ],
        }

        # Calculate the maximum width for formatting
        max_label_length = max(len(label) for section in info_sections.values() for label, _ in section)
        max_section_length = max(len(section) for section in info_sections)
        separator_length = max(max_label_length + 25, max_section_length + 10)

        # Log the information
        logger.info(
            "Scene Configuration Details",
            scene_name=self.__class__.__name__,
            output_mode=self.mode,
            frame_dimensions=f"{config.frame_width:.2f}x{config.frame_height:.2f}",
            background_style=self._background_style.value,
            color_scheme=self._color_scheme.value,
            gradient_enabled=self._gradient,
        )

        # Print formatted information
        print("\n" + "=" * separator_length)  # noqa: T201
        for section, items in info_sections.items():
            print(f"\n{section}:")
            print("-" * len(section))
            for label, value in items:
                print(f"{label:<{max_label_length}} : {value}")
        print("\n" + "=" * separator_length + "\n")

    @lru_cache(maxsize=32)  # noqa: B019
    def _get_animation_timings(self, total_chars: int, duration: float) -> tuple[float, float, float]:
        """Cached calculation of animation timings."""
        write_time = min(duration * 0.35, total_chars * 0.04)
        scale_time = min(duration * 0.1, 0.3)
        display_time = max(0, duration - (2 * write_time) - scale_time)
        return write_time, scale_time, display_time

    def create_text_mobject(self, text: str, font_size: int, is_verse: bool = True) -> Text:
        """Create a Text mobject with proper font handling."""
        color = self.color_scheme[-1]  # Use the last color in the scheme for text
        font_path = self.font_path if is_verse else self.font_path_info
        font_helper = FontHelper(str(font_path))
        if self.font_path:
            with register_font(font_path):
                normalized_text = font_helper.process_text(text) if font_helper else text
                return Text(normalized_text, font=font_helper.get_font_name(), font_size=font_size, color=color)
        else:
            return Text(text, font_size=font_size, color=color)

    def calculate_average_char_width(self, text: str) -> float:
        """Calculates the average character width of a font."""
        if not text:
            raise ValueError("Input text cannot be empty")

        try:
            pygame.font.init()  # initialize only the font module.
            font = pygame.font.Font(self.font_path, self.font_size)
            # total_width = sum(font.render(char, True, (0, 0, 0)).get_width() for char in text)
            total_width = sum(font.size(char)[0] for char in text)  # This is more efficient as it doesn't need to render the text.
            average_width = total_width / len(text)
            pygame.quit()
        except Exception as e:
            raise RuntimeError(f"Error calculating average character width: {e!s}")

        return average_width

    def wrap_text(self, text) -> list[str]:
        """Wrap the input text to fit within the screen width."""
        screen_width = config.pixel_width
        width_percentage = 0.6

        # Calculate maximum width in pixels
        max_pixel_width = screen_width * width_percentage
        avg_char_width = self.calculate_average_char_width(text)

        # Calculate maximum width in characters
        max_char_width = int(max_pixel_width // avg_char_width)

        return textwrap.wrap(text, max_char_width)

    def create_verse_info(self) -> Text:
        """Create a Text mobject for the verse information."""
        verse_info = self.create_text_mobject(self.verse_info, self.info_font_size, False)

        margins = {"widescreen": 0.1, "vertical": 0.15, "square": 0.12}
        bottom_margin = config.frame_height * margins.get(self.screen_type, 0.1)

        verse_info.to_edge(DOWN).shift(UP * bottom_margin)

        return verse_info

    def create_verse_text(self, verse: str) -> Text:
        """Create a Text mobject for the verse."""
        return self.create_text_mobject(verse, self.font_size)

    def add_audio_to_video(self, audio_path):
        if self.audio_paths and self.mode.lower() == "video":
            self.add_sound(audio_path)

    def construct(self):
        """Construct the scene by creating and animating the background and verses."""
        logger.info("Starting scene construction", total_verses=len(self.verses), total_duration=sum(self.durations))
        super().construct()

        verse_info = self.create_verse_info()
        self.add(verse_info)

        # Create VGroups for each verse, including wrapped lines
        verse_groups = []
        for i, verse in enumerate(self.verses, 1):
            try:
                splitted_verse = self.wrap_text(verse)
                text_mobjects = [self.create_verse_text(line) for line in splitted_verse]
                verse_group = VGroup(*text_mobjects)
                verse_group.arrange(DOWN, aligned_edge=ORIGIN, buff=0.2)
                max_width = max(t.width for t in verse_group)
                verse_group.set(width=min(max_width, config.frame_width - 1))
                verse_group.move_to(ORIGIN)
                verse_groups.append(verse_group)

                logger.info("Verse processed successfully", verse_number=i, lines_count=len(splitted_verse))
            except Exception as e:
                logger.exception("Error processing verse", verse_number=i, error=str(e), exc_info=True)
                raise

        if self.mode.lower() == "video":
            self.add_audio_to_video(self.audio_paths)

            # Process verses with high-performance animations
            batch_size = 8  # Increased batch size
            frame_skip = 2  # Skip frames for performance

            for verse_idx, (verse_group, duration) in enumerate(zip(verse_groups, self.durations, strict=False)):
                write_anims, scale_anim, unwrite_anims, scale_time = create_high_performance_animations(
                    verse_group, duration, batch_size=batch_size, frame_skip=frame_skip
                )

                # Execute optimized animations
                self.play(AnimationGroup(*write_anims, lag_ratio=0.02))
                self.play(scale_anim, run_time=scale_time)

                # Calculate and apply display time
                total_chars = sum(len(text.text) for text in verse_group)
                _, _, display_time = self._get_animation_timings(total_chars, duration)

                if display_time > 0:
                    self.wait(display_time)

                self.play(AnimationGroup(*unwrite_anims, lag_ratio=0.02))

            self.wait(0.5)
        else:
            # Image mode - just add the verses
            for verse_group in verse_groups:
                self.add(verse_group)


if __name__ == "__main__":
    verses = [
        "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ ﰀ",
    ]
    verse_info = "Al-Fātiḥah"
    durations = [5.564081632653061]
    font_path = "assets/fonts/UthmanicHafs_v22/uthmanic_hafs_v22.ttf"
    font_path_info = "assets/fonts/Amiri/Amiri-Regular.ttf"

    scene = QuranVerseScene(
        verses=verses,
        verse_info=verse_info,
        durations=durations,
        background_style=BackgroundStyle.STAR_MOTIF_GEOMETRIC,
        color_scheme=ColorScheme.PRAYER_NIGHT,
        gradient=True,
        gradient_direction=UP,
        font_path=font_path,
        mode="video",
        aspect_ratio="16:9",
        audio_paths=["temp/audio/Abdullah_Basfar_192kbps/001001.mp3"],
        font_path_info=font_path_info,
    )
    scene.render(preview=True)
