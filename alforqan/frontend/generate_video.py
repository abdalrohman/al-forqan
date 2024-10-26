"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from pathlib import Path
import shutil

from alforqan.backend.core.backgrounds import BackgroundStyle
from alforqan.backend.core.color_scheme import ColorScheme
from alforqan.backend.core.quran_manim_scene import QuranVerseScene
from alforqan.backend.utils.font_helper import FontHelper
from alforqan.frontend.custom_component.status import *

from manim import ORIGIN
import streamlit as st


def generate_video(
    verse_info,
    final_durations,
    full_surah_output,
    visualization_config,
    app_config,
    temp_directory,
    output_directory,
    verse_range,
):
    """Generate video with the processed audio and visualization settings"""
    with st.status("Rendering scene...", expanded=True) as status:
        try:
            # Prepare verse data
            verse_texts = [item["aya_text"] for item in verse_info["verse_info"]]
            verse_data = verse_info["verse_info"][0]
            verse_info_text = f"{verse_data['sura_name_en']} ({verse_data['sura_name_ar']})"

            status.update(
                label="""Initializing video generation...""",
            )

            progress_bar = st.progress(0, text="Initializing scene...")

            if not visualization_config:
                show_error("Can't continue: visual settings not set")
                return False

            # Ensure the font installed on the system before enter the scene
            # Important step before generate the video
            FontHelper(app_config.get("fonts.font_path")).install()
            FontHelper(app_config.get("fonts.font_info_path")).install()

            # Create and render scene
            scene = QuranVerseScene(
                verses=verse_texts,
                verse_info=verse_info_text,
                durations=final_durations,
                background_style=BackgroundStyle(visualization_config["background"]),
                color_scheme=ColorScheme(visualization_config["color_scheme"]),
                gradient=visualization_config["gradient"],
                gradient_direction=ORIGIN,
                font_path=app_config.get("fonts.font_path"),
                mode=visualization_config["mode"],
                aspect_ratio=visualization_config["aspect_ratio"],
                audio_paths=str(full_surah_output),
                font_path_info=app_config.get("fonts.font_info_path"),
                quality=visualization_config["video_quality"],
                output_dir=str(temp_directory),
                output_file=verse_range.output_filename,
            )

            progress_bar.progress(0.5, text="Scene created, starting render...")

            status.update(
                label="""Generating final video...""",
            )

            scene.render(preview=visualization_config["preview"])
            progress_bar.progress(1.0, text="✨ Render complete!")

            # Move output file
            output_file = temp_directory / Path("video_dir") / f"{verse_range.output_filename}.mp4"
            if output_file.exists():
                shutil.move(str(output_file), str(output_directory / output_file.name))
                return True
        except Exception as e:
            show_error(f"Error generating video: {str(e)}")
            return False

        return False
