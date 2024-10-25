"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

import streamlit as st


def create_metrics_grid(metrics: list[dict[str, str | int | float]], columns: int = 3) -> None:
    """Create a grid of metric cards.

    Args:
        metrics: List of dictionaries containing 'label' and 'value' keys
        columns: Number of columns in the grid (default: 3)
    """
    # Calculate the number of rows needed
    n_metrics = len(metrics)
    n_rows = (n_metrics + columns - 1) // columns

    # Create the grid layout
    for row in range(n_rows):
        cols = st.columns(columns)
        for col in range(columns):
            idx = row * columns + col
            if idx < n_metrics:
                metric = metrics[idx]
                cols[col].markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{metric['value']}</div>
                        <div class="metric-label">{metric['label']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def create_data_container(title: str, content: str, custom_styles: str | None = None) -> None:
    """Create a container for displaying data with a gradient background.

    Args:
        title: The container title
        content: HTML content to display inside the container
        custom_styles: Optional additional CSS styles
    """
    styles = f"style='{custom_styles}'" if custom_styles else ""
    st.markdown(
        f"""
        <div class="data-container" {styles}>
            <div class="container-title">{title}</div>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_empty_state(message: str, emoji: str = "📝", custom_styles: str | None = None) -> None:
    """Create an empty state message with an emoji.

    Args:
        message: The message to display
        emoji: The emoji to show (default: 📝)
        custom_styles: Optional additional CSS styles
    """
    styles = f"style='{custom_styles}'" if custom_styles else ""
    st.markdown(
        f"""
        <div class="empty-state" {styles}>
            <div style="font-size: 2rem; margin-bottom: 1rem;">{emoji}</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
