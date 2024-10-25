"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib

from alforqan.backend.utils.every_ayah_downloader import QuranAudioDownloader
from alforqan.frontend.custom_component.data_display import create_empty_state, create_metrics_grid
from alforqan.frontend.custom_component.status import show_error
from alforqan.frontend.custom_component.step_header import (
    create_stp_header,
)

import pandas as pd
import streamlit as st

MAX_TABLE_HEIGHT = 500
TABLE_HEIGHT_THRESHOLD = 10


@dataclass
class QuranicVerseRange:
    """Data class to store Quranic verse range information for audio processing"""

    reciter_id: int
    reciter_name: str
    surah_number: int
    start_verse: int
    end_verse: int
    output_filename: str
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()  # noqa: DTZ005

    def generate_unique_id(self) -> str:
        """Generate a unique identifier for the verse range"""
        key_string = f"{self.reciter_id}_{self.surah_number}_{self.start_verse}_{self.end_verse}"
        return hashlib.sha256(key_string.encode()).hexdigest()


class QuranicVerseProcessor:
    """Manages the processing queue for Quranic verses"""

    def __init__(self):
        self._initialize_session_state()

    @staticmethod
    def _initialize_session_state():
        """Initialize or reset the Streamlit session state"""
        if "verse_queue" not in st.session_state:
            st.session_state.verse_queue = {}
        if "processing_queue" not in st.session_state:
            st.session_state.processing_queue = set()

    @staticmethod
    def clear_all_queues():
        """Reset all processing queues"""
        st.session_state.verse_queue = {}
        st.session_state.processing_queue = set()

    @staticmethod
    def clear_processing_queue():
        """Reset only the processing queue"""
        st.session_state.processing_queue = set()

    @staticmethod
    def add_verse_range(verse_range: QuranicVerseRange) -> bool:
        """Add a new verse range to the queue if not duplicate"""
        unique_id = verse_range.generate_unique_id()
        if unique_id not in st.session_state.verse_queue:
            st.session_state.verse_queue[unique_id] = verse_range
            st.session_state.processing_queue.add(unique_id)
            return True
        return False

    @staticmethod
    def get_pending_verses() -> dict[str, QuranicVerseRange]:
        """Retrieve all pending verse ranges"""
        return {key: verse_range for key, verse_range in st.session_state.verse_queue.items() if key in st.session_state.processing_queue}

    @staticmethod
    def mark_completed(unique_id: str):
        """Mark a verse range as processed"""
        if unique_id in st.session_state.processing_queue:
            st.session_state.processing_queue.remove(unique_id)

    @staticmethod
    def get_queue_statistics() -> dict:
        """Get current queue statistics"""
        return {
            "total_verses": len(st.session_state.verse_queue),
            "pending_verses": len(st.session_state.processing_queue),
            "completed_verses": len(st.session_state.verse_queue) - len(st.session_state.processing_queue),
        }

    @staticmethod
    def get_queue_dataframe() -> pd.DataFrame:
        """Convert verse queue to a displayable DataFrame"""
        if not st.session_state.verse_queue:
            return pd.DataFrame()

        queue_data = []
        for unique_id, verse_range in st.session_state.verse_queue.items():
            processing_status = "🔄 Pending" if unique_id in st.session_state.processing_queue else "✅ Completed"
            queue_data.append(
                {
                    "Surah": verse_range.surah_number,
                    "Starting Verse": verse_range.start_verse,
                    "Ending Verse": verse_range.end_verse,
                    "Reciter": verse_range.reciter_name,
                    "Status": processing_status,
                    "Added On": datetime.fromisoformat(verse_range.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": unique_id,
                }
            )

        df = pd.DataFrame(queue_data)
        if not df.empty:
            df["sort_priority"] = df["Status"].map({"🔄 Pending": 0, "✅ Completed": 1})
            df = df.sort_values(["sort_priority", "Added On"], ascending=[True, False])
            df = df.drop("sort_priority", axis=1)

        return df


# Initialize processors
audio_processor = QuranAudioDownloader()
verse_processor = QuranicVerseProcessor()


@st.cache_data(show_spinner=False)
def fetch_available_reciters() -> list[dict]:
    """Fetch and cache available Quran reciters"""
    try:
        reciters = audio_processor.list_available_reciters()
        return sorted(reciters, key=lambda x: x["name"])
    except Exception as e:
        show_error(f"Failed to retrieve reciters: {str(e)}")
        return []


def display_processing_queue():
    """Display the verse processing queue with enhanced visualization"""
    queue_stats = verse_processor.get_queue_statistics()

    # Queue Overview Section
    create_stp_header(1, "Queue Overview")

    metrics = [
        {
            "label": "Total Verses",
            "value": queue_stats["total_verses"],
        },
        {
            "label": "Pending Processing",
            "value": queue_stats["pending_verses"],
        },
        {
            "label": "Completed",
            "value": queue_stats["completed_verses"],
        },
    ]
    create_metrics_grid(metrics)

    # Queue Table Section
    queue_df = verse_processor.get_queue_dataframe()

    if not queue_df.empty:
        create_stp_header(2, "Processing Queue")

        # Style the status column
        def style_status_column(row):
            styles = []
            for val in row:
                if val == "🔄 Pending":
                    styles.append("background-color: #084298;")  # Blue background for pending
                else:
                    styles.append("background-color: #0a3622;")  # Green background for completed
            return styles

        # Prepare and style the dataframe
        display_df = queue_df.drop(columns=["ID"])
        styled_df = display_df.style.apply(style_status_column, subset=["Status"])

        # Additional styling for the entire dataframe
        styled_df = styled_df.set_properties(
            **{
                "color": "#D1D5DB",
            }
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=MAX_TABLE_HEIGHT if len(queue_df) > TABLE_HEIGHT_THRESHOLD else None,
        )

    else:
        create_empty_state("The processing queue is empty. Add verses using the form above.")
