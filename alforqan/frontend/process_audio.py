"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from alforqan.backend.quran_data.audio_processor import AudioProcessor
from alforqan.frontend.custom_component.status import show_error, show_success

import streamlit as st


def process_audio_files(verse_info, audio_directory, status):
    """Process audio files for the verses"""
    verse_data = verse_info["verse_info"][0]
    full_surah_output = audio_directory / f"{verse_data['sura_name_en']}.mp3"

    with AudioProcessor() as audio_processor:
        durations = []
        processed_files = []

        # Create a progress container
        progress_container = st.container()

        # Process individual audio files
        for i, path in enumerate(verse_info["verses_audio_paths"]):
            status.update(label=f"Processing Audio: File {i + 1} of {len(verse_info['verses_audio_paths'])}")

            with progress_container:
                progress_text = f"Processing verse {i + 1}"
                progress_bar = st.progress(0, text=progress_text)

            try:
                # Audio processing steps
                normalized_audio = audio_processor.normalize_audio(path)
                progress_bar.progress(0.33, text=f"{progress_text} - Normalized")

                processed_file_info = audio_processor.create_with_preset("conservative").preprocess_audio(normalized_audio)
                progress_bar.progress(0.66, text=f"{progress_text} - Processed")

                durations.append(processed_file_info["duration"])
                processed_files.append(processed_file_info["path"])

                progress_bar.progress(1.0, text=f"{progress_text} - Complete")
            except Exception as e:
                show_error(f"Error processing audio: {str(e)}")
                return None

        # Merge processed files
        status.update(label="Combining processed audio files...")

        merge_info = audio_processor.merge_audio_files(processed_files, full_surah_output)
        final_durations = [change["effective_duration_ms"] / 1000 for change in merge_info["duration_changes"]]

        show_success("Audio processing completed successfully!")
        return full_surah_output, final_durations
