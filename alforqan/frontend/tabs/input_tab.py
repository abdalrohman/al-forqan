"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from alforqan.backend.core.backgrounds import BackgroundStyle
from alforqan.backend.core.backgrounds.gradient_direction import ManimDirections
from alforqan.backend.core.color_scheme import ColorScheme
from alforqan.backend.utils.utils import sanitize_name
from alforqan.frontend.custom_component.step_header import create_stp_header
from alforqan.frontend.process_verses import QuranicVerseRange, fetch_available_reciters, verse_processor

from manim import constants
import streamlit as st
import structlog

logger = structlog.get_logger(__name__)


def input_tab(app_config, visualization_config):
    create_stp_header(1, "Select Reciter")
    available_reciters = fetch_available_reciters()
    reciter_display_options = [f"{r['name']} ({r['quality']})" for r in available_reciters]
    selected_reciter_option = st.selectbox(
        "Available Reciters",
        options=reciter_display_options,
        index=0 if reciter_display_options else 0,
        help="Choose a reciter for the verse audio",
    )

    selected_reciter_name = (
        reciter_display_options[reciter_display_options.index(selected_reciter_option)] if reciter_display_options else None
    )
    reciter_id = available_reciters[reciter_display_options.index(selected_reciter_option)]["id"] if reciter_display_options else None

    create_stp_header(2, "Select Verses")
    verse_col1, verse_col2, verse_col3 = st.columns(3)

    with verse_col1:
        surah_number = st.number_input(
            "Surah Number",
            min_value=1,
            max_value=114,
            value=1,
            help="Enter the Surah number (1-114)",
        )

    with verse_col2:
        verse_start = st.number_input(
            "Starting Verse",
            min_value=1,
            value=1,
            help="Select the first verse",
        )

    with verse_col3:
        verse_end = st.number_input(
            "Ending Verse",
            min_value=verse_start,
            value=verse_start,
            help="Select the last verse",
        )

    # Step 3: Visualization Settings
    create_stp_header(3, "Customize Visualization")
    visual_col1, visual_col2, visual_col3 = st.columns(3)

    with visual_col1:
        background_style = st.selectbox(
            "Background Theme",
            options=[style.value for style in BackgroundStyle],
            index=list(BackgroundStyle).index(BackgroundStyle(app_config.get("background.background"))),
            help="Choose the background style for your video",
        )
        visualization_config["background"] = background_style

    with visual_col2:
        color_theme = st.selectbox(
            "Color Theme",
            options=[scheme.value for scheme in ColorScheme],
            index=list(ColorScheme).index(ColorScheme(app_config.get("color_scheme.color_scheme"))),
            help="Select the color scheme for text and elements",
        )
        visualization_config["color_scheme"] = color_theme

    with visual_col3:
        render_quality = st.selectbox(
            "Output Quality",
            options=constants.QUALITIES.keys(),
            index=list(constants.QUALITIES.keys()).index("production_quality"),
            help="Set the video rendering quality",
        )
        visualization_config["video_quality"] = render_quality

    enable_gradient = st.checkbox(
        "Enable Color Gradient",
        value=True,
        help="Apply a gradient effect to the text",
    )
    visualization_config["gradient"] = enable_gradient
    if enable_gradient:
        dir_col, inten_col = st.columns(2)
        with dir_col:
            directions = ManimDirections().get_streamlit_options()

            # Define a format function to display the second element of the tuple
            def format_direction(x):
                return x[1]  # Return the description part of the tuple

            gradient_direction = st.selectbox(
                "Gradient Directions",
                options=directions,
                format_func=format_direction,
                index=1,
            )
            gradient_direction = gradient_direction[0]  # Get just the direction name
        with inten_col:
            gradient_intensity = st.slider("Gradient intensity", min_value=0.0, max_value=1.0, value=0.3)
        visualization_config.update(
            {
                "gradient_direction": gradient_direction,
                "gradient_intensity": gradient_intensity,
            }
        )

    # Advanced configuration options
    aspect_ratios = ["16:9", "9:16", "4:3", "1:1", "12:12"]
    output_modes = ["video", "image"]

    with st.expander("Advanced Settings"):
        mode_col, ratio_col = st.columns(2)
        with mode_col:
            output_mode = st.selectbox(
                "Output Format",
                output_modes,
                index=output_modes.index(app_config.get("scene_settings.mode")),
                help="Choose between video or image output",
            )
        with ratio_col:
            video_ratio = st.selectbox(
                "Aspect Ratio",
                aspect_ratios,
                index=aspect_ratios.index(app_config.get("scene_settings.aspect_ratio")),
                help="Select the video dimensions ratio",
            )
        renderer = st.selectbox(
            "Choose the renderer",
            ["cairo", "opengl"],
            help="Select 'opengl' for better performance on compatible systems. Default 'cairo' works on all systems but may be slower.",
        )
        logger.info("Chosen renderer", renderer=renderer)

        visualization_config.update(
            {
                "mode": output_mode,
                "aspect_ratio": video_ratio,
                "renderer": renderer,
            }
        )

    # Action buttons with improved layout
    create_stp_header(4, "Process")
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("➕ Add to Queue", type="primary", use_container_width=True):
            verse_range = QuranicVerseRange(
                reciter_id=reciter_id,
                reciter_name=selected_reciter_name,
                surah_number=surah_number,
                start_verse=verse_start,
                end_verse=verse_end,
                output_filename=(
                    f"{sanitize_name(selected_reciter_name)}_"
                    f"surah_{surah_number:03d}_"
                    f"verse_{verse_start:03d}"
                    f"{f'_to_{verse_end:03d}' if verse_end != verse_start else ''}"
                    f"_{background_style}"
                    f"_{color_theme}"
                    f"_{render_quality}"
                    f"_{video_ratio}"
                ),
            )

            if verse_processor.add_verse_range(verse_range):
                st.success("✅ Successfully added to queue!")
            else:
                st.warning("⚠️ These verses are already queued")

            # Switch the tab here

    with action_col2:
        if st.button("🗑️ Clear Queue", use_container_width=True):
            verse_processor.clear_all_queues()
            st.success("🧹 Queue cleared successfully!")
            st.rerun()

    with action_col3:
        if st.button("🔄 Reset Pending", use_container_width=True):
            verse_processor.clear_processing_queue()
            st.success("🔄 Pending items reset!")
            st.rerun()
