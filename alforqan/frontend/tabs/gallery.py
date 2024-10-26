"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from datetime import datetime
import io
from pathlib import Path

from alforqan.frontend.custom_component.cards import create_iconic_card
from alforqan.frontend.custom_component.data_display import create_metrics_grid
from alforqan.frontend.custom_component.header import create_header_section

import streamlit as st


def get_video_data(video_path: Path) -> tuple:
    """Helper function to get video data efficiently"""
    stats = video_path.stat()
    file_size = stats.st_size / (1024 * 1024)  # Convert to MB
    modified_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
    return file_size, modified_time


def read_video_bytes(video_path: Path) -> io.BytesIO:
    """Efficiently read video file into memory"""
    buffer = io.BytesIO()
    chunk_size = 8192  # 8KB chunks for efficient memory usage

    with open(video_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            buffer.write(chunk)

    buffer.seek(0)
    return buffer


def display_video_gallery(output_directory):
    """Display generated videos in an enhanced grid layout with metadata and actions"""
    videos = list(output_directory.glob("*.mp4"))

    # Header section with stats
    create_header_section("Video Gallery", "Browse and manage your generated visualizations")

    if not videos:
        create_iconic_card("🎬", "No Videos Yet", "Generated videos will appear here. Start by creating your first visualization!")
        return

    # Calculate statistics
    total_videos = len(videos)
    total_size = sum(video.stat().st_size for video in videos) / (1024 * 1024)

    if videos:
        modification_times = [video.stat().st_mtime for video in videos]
        newest = max(modification_times)
        oldest = min(modification_times)
        days_active = (newest - oldest) / 86400
    else:
        days_active = 0

    gallery_stats = [
        {"label": "Total Videos", "value": total_videos},
        {"label": "Total Size (MB)", "value": f"{total_size:.1f}"},
        {"label": "Days Active", "value": f"{days_active:.1f}"},
    ]
    create_metrics_grid(gallery_stats)

    # Sort videos by creation time (newest first)
    videos.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Grid layout with caching for performance
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def get_cached_video_data(video_path: Path):
        return get_video_data(video_path)

    # Display videos in grid
    num_videos = len(videos)
    cols_per_row = min(3, num_videos)

    for i in range(0, num_videos, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < num_videos:
                with col:
                    video_path = videos[i + j]
                    file_size, modified_time = get_cached_video_data(video_path)

                    # Video player
                    st.video(str(video_path))

                    st.markdown(
                        f"""
                        <div class="video-metadata">
                            <div class="metadata-item">
                                <span class="metadata-label">Name:</span>
                                <span class="metadata-value">{video_path.stem[:20]}...</span>
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
                    video_bytes = read_video_bytes(video_path)
                    st.download_button(
                        "Download",
                        video_bytes,
                        file_name=f"{video_path.stem}.mp4",
                        key=f"download_{video_path.stem}",
                        use_container_width=True,
                        icon="⬇️",
                    )
