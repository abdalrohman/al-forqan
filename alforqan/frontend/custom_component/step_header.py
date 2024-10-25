"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

import streamlit as st


def create_stp_header(number: int, title: str, custom_styles: str | None = None) -> None:
    """Create a numbered section header with hover effects.

    Args:
        number: The section number
        title: The section title
        custom_styles: Optional additional CSS styles
    """
    styles = f"style='{custom_styles}'" if custom_styles else ""
    st.markdown(
        f"""
        <div class="section-header" {styles}>
            <div class="number-badge">{number}</div>
            <h2>{title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
