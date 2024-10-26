"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
import shutil

from alforqan.backend.utils.logging import LogConfig
from alforqan.config import Config
from alforqan.frontend.custom_component.status import *
from alforqan.frontend.generate_video import generate_video
from alforqan.frontend.get_verse_info import get_verse_info
from alforqan.frontend.process_audio import process_audio_files
from alforqan.frontend.process_verses import display_processing_queue, verse_processor
from alforqan.frontend.tabs.about import display_about_section
from alforqan.frontend.tabs.gallery import display_media_gallery
from alforqan.frontend.tabs.input_tab import input_tab

import streamlit as st

# Initialize configuration
app_config = Config("config.toml")
log_config = LogConfig(
    app_config.get("settings.log_path"),
    log_level=app_config.get("settings.log_level"),
    environment=app_config.get("settings.environment"),
    filters=app_config.get("settings.filters"),
)
app_logger = log_config.get_logger()

# Page configuration
st.set_page_config(
    page_title="Al-Forqan | Quranic Video Generation",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "verse_queue" not in st.session_state:
    st.session_state.verse_queue = {}
if "processing_queue" not in st.session_state:
    st.session_state.processing_queue = set()


def apply_global_styles(file_name: str) -> None:
    if not Path(file_name).exists():
        st.error("Style sheet not found...")
        st.stop()
    with open(file_name) as f:
        st.html(f"<style>{f.read()}</style>")


# Apply css styles
apply_global_styles("alforqan/frontend/css/base.css")
apply_global_styles("alforqan/frontend/css/components/header.css")
apply_global_styles("alforqan/frontend/css/components/buttons.css")
apply_global_styles("alforqan/frontend/css/components/checkbox.css")
apply_global_styles("alforqan/frontend/css/components/disable.css")
apply_global_styles("alforqan/frontend/css/components/input.css")
apply_global_styles("alforqan/frontend/css/components/tabs.css")
apply_global_styles("alforqan/frontend/css/components/progress.css")
apply_global_styles("alforqan/frontend/css/components/step_header.css")
apply_global_styles("alforqan/frontend/css/components/data_display.css")
apply_global_styles("alforqan/frontend/css/components/cards.css")
apply_global_styles("alforqan/frontend/css/components/section.css")
apply_global_styles("alforqan/frontend/css/components/metadata.css")
apply_global_styles("alforqan/frontend/css/components/video.css")

# Application Header
st.markdown(
    """
    <div class="header-container">
        <h1 class="app-title">بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيم</h1>
        <p class="app-description">
            <span class="highlight">Al-Forqan</span>: Transform Quranic verses into stunning visual experiences with professional-grade
            video generation and customizable styles
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


class OutputPaths(str, Enum):
    """Enumeration of output directory paths"""

    TEMPORARY = "alforqan_temp"
    OUTPUT = "generated"
    AUDIO_FILES = "audio"


# Initialize directory structure
base_directory = Path(".")
temp_directory = base_directory / OutputPaths.TEMPORARY.value
output_directory = base_directory / OutputPaths.OUTPUT.value
audio_directory = temp_directory / OutputPaths.AUDIO_FILES.value

# Create required directories
for dir_path in [temp_directory, output_directory, audio_directory]:
    dir_path.mkdir(parents=True, exist_ok=True)


def cleanup_temporary_files():
    """Clean up temporary processing files"""
    try:
        if temp_directory.exists():
            shutil.rmtree(temp_directory)
        temp_directory.mkdir(parents=True, exist_ok=True)
        audio_directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        show_error(f"Error during cleanup: {str(e)}")


visualization_config = {}


# TODO generate the audio based on the media type
def main():
    """Main application logic with enhanced UI organization"""
    # Create main application sections
    tabs = st.tabs(
        ["📥 Create New", "⚙️ Processing Queue", "🎬 Gallery", "ℹ️ About"],
    )
    with tabs[0]:
        input_tab(app_config, visualization_config)

    with tabs[1]:
        display_processing_queue()

        if st.button("▶️ Start Processing", type="primary", use_container_width=True):
            pending_verses = verse_processor.get_pending_verses()

            if pending_verses:
                progress_bar = st.progress(0)
                st.write(f"📊 Processing {len(pending_verses)} verse ranges...")

                for idx, (verse_id, verse_range) in enumerate(pending_verses.items()):
                    try:
                        with st.status("Processing verses...", expanded=True) as status:
                            verse_info = get_verse_info(verse_range, app_config, audio_directory, status)
                            full_surah_output, final_durations = process_audio_files(verse_info, audio_directory, status)

                        success = generate_video(
                            verse_info,
                            final_durations,
                            full_surah_output,
                            visualization_config,
                            app_config,
                            temp_directory,
                            output_directory,
                            verse_range,
                        )
                        if success:
                            verse_processor.mark_completed(verse_id)
                            cleanup_temporary_files()
                        progress_bar.progress((idx + 1) / len(pending_verses))
                    except Exception as e:
                        st.error(f"Error processing verse range: {str(e)}")

                show_success("Processing completed successfully!")
            else:
                show_info("No pending verses to process")

    with tabs[2]:
        display_media_gallery(output_directory)

    with tabs[3]:
        display_about_section(app_config)


if __name__ == "__main__":
    main()
