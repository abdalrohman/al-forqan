"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

import streamlit as st


def create_header_section(
    title: str,
    description: str,
    variant: str = "default",
    custom_styles: str | None = None,
) -> None:
    """Create a header section with title and description.

    Args:
        title: Header title
        description: Header description
        variant: Style variant (default: "default")
        custom_styles: Optional additional CSS styles
    """
    styles = f"style='{custom_styles}'" if custom_styles else ""

    st.markdown(
        f"""
        <div class="header-section header-section--{variant}" {styles}>
            <h1 class="header-title">{title}</h1>
            <p class="header-description">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
