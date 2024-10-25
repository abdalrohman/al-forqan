"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from alforqan.backend.quran_data.quran_data_manager import QuranDataManager

import streamlit as st


def get_verse_info(verse_range, app_config, audio_directory, status):
    """Fetch verse information from QuranDataManager"""
    status.update(
        label=f"Processing verses: Surah {verse_range.surah_number}: Verses {verse_range.start_verse} - {verse_range.end_verse}",
    )

    quran_manager = QuranDataManager(
        quran_data_filepath=app_config.get("quran_data.json_data_file"),
        audio_directory=str(audio_directory),
    )

    verse_info = quran_manager.get_verses_info(
        reciter_id=int(verse_range.reciter_id),
        surah_number=verse_range.surah_number,
        start_ayah=verse_range.start_verse,
        end_ayah=verse_range.end_verse,
    )

    if verse_info:
        st.toast(f"✅ Processed verses {verse_range.start_verse}-{verse_range.end_verse}")
    return verse_info
