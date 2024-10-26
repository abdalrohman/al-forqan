"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from datetime import datetime
import io
from pathlib import Path
from typing import Literal

from alforqan.frontend.custom_component.cards import create_iconic_card
from alforqan.frontend.custom_component.data_display import create_metrics_grid
from alforqan.frontend.custom_component.header import create_header_section

import streamlit as st

MediaType = Literal["video", "image"]

SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".webm"}
SUPPORTED_IMAGE_FORMATS = {".png"}


def get_media_type(file_path: Path) -> MediaType:
    """Determine if the file is a video or image based on extension"""
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_VIDEO_FORMATS:
        return "video"
    elif suffix in SUPPORTED_IMAGE_FORMATS:
        return "image"
    raise ValueError(f"Unsupported file format: {suffix}")


def get_media_data(media_path: Path) -> tuple:
    """Helper function to get media file data efficiently"""
    stats = media_path.stat()
    file_size = stats.st_size / (1024 * 1024)  # Convert to MB
    modified_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
    media_type = get_media_type(media_path)
    return file_size, modified_time, media_type


def read_media_bytes(media_path: Path) -> io.BytesIO:
    """Efficiently read media file into memory"""
    buffer = io.BytesIO()
    chunk_size = 8192  # 8KB chunks for efficient memory usage

    with open(media_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            buffer.write(chunk)

    buffer.seek(0)
    return buffer


def display_media_gallery(output_directory: Path):
    """Display generated videos and images in an enhanced grid layout with metadata and actions"""
    # Find all supported media files
    media_files = []
    for format_group in [SUPPORTED_VIDEO_FORMATS, SUPPORTED_IMAGE_FORMATS]:
        for ext in format_group:
            media_files.extend(output_directory.glob(f"*{ext}"))

    # Header section with stats
    create_header_section("Media Gallery", "Browse and manage your generated visualizations")

    if not media_files:
        create_iconic_card(
            "🎬", "No Media Files Yet", "Generated videos and images will appear here. Start by creating your first visualization!"
        )
        return

    # Calculate statistics
    total_files = len(media_files)
    total_size = sum(file.stat().st_size for file in media_files) / (1024 * 1024)
    video_count = sum(1 for f in media_files if get_media_type(f) == "video")
    image_count = sum(1 for f in media_files if get_media_type(f) == "image")

    if media_files:
        modification_times = [file.stat().st_mtime for file in media_files]
        newest = max(modification_times)
        oldest = min(modification_times)
        days_active = (newest - oldest) / 86400
    else:
        days_active = 0

    gallery_stats = [
        {"label": "Total Files", "value": total_files},
        {"label": "Videos", "value": video_count},
        {"label": "Images", "value": image_count},
        {"label": "Total Size (MB)", "value": f"{total_size:.1f}"},
        {"label": "Days Active", "value": f"{days_active:.1f}"},
    ]
    create_metrics_grid(gallery_stats)

    # Sort files by creation time (newest first)
    media_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Grid layout with caching for performance
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def get_cached_media_data(media_path: Path):
        return get_media_data(media_path)

    # Display media files in grid
    num_files = len(media_files)
    cols_per_row = min(3, num_files)

    for i in range(0, num_files, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < num_files:
                with col:
                    media_path = media_files[i + j]
                    file_size, modified_time, media_type = get_cached_media_data(media_path)

                    # Display media based on type
                    if media_type == "video":
                        st.video(str(media_path))
                    else:  # image
                        st.image(str(media_path), use_column_width=True)

                    # Display metadata
                    st.markdown(
                        f"""
                        <div class="media-metadata">
                            <div class="metadata-item">
                                <span class="metadata-label">Name:</span>
                                <span class="metadata-value">{media_path.stem[:10]}...</span>
                            </div>
                            <div class="metadata-item">
                                <span class="metadata-label">Type:</span>
                                <span class="metadata-value">{media_type.capitalize()}</span>
                            </div>
                            <div class="metadata-item">
                                <span class="metadata-label">Size:</span>
                                <span class="metadata-value">{file_size:.1f} MB</span>
                            </div>
                            <div class="metadata-item">
                                <span class="metadata-label">Creation date:</span>
                                <span class="metadata-value">{modified_time}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Download button
                    media_bytes = read_media_bytes(media_path)
                    st.download_button(
                        "Download",
                        media_bytes,
                        file_name=f"{media_path.name}",
                        key=f"download_{media_path.stem}",
                        use_container_width=True,
                        icon="⬇️",
                    )
