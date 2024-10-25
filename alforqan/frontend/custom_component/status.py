"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

import streamlit as st


def show_success(message: str, custom_styles: str | None = None) -> None:
    """Display a success status notification.

    Args:
        message: The success message to display
        custom_styles: Optional additional CSS styles
    """
    styles = custom_styles or ""
    st.markdown(
        f"""
        <div class="status status--success fadeIn" style="{styles}">
            ✅ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_error(message: str, custom_styles: str | None = None) -> None:
    """Display an error status notification.

    Args:
        message: The error message to display
        custom_styles: Optional additional CSS styles
    """
    styles = custom_styles or ""
    st.markdown(
        f"""
        <div class="status status--error fadeIn" style="{styles}">
            ❌ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_info(message: str, custom_styles: str | None = None) -> None:
    """Display an info status notification.

    Args:
        message: The information message to display
        custom_styles: Optional additional CSS styles
    """
    styles = custom_styles or ""
    st.markdown(
        f"""
        <div class="status status--info fadeIn" style="{styles}">
            ℹ️ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_warning(message: str, custom_styles: str | None = None) -> None:
    """Display a warning status notification.

    Args:
        message: The warning message to display
        custom_styles: Optional additional CSS styles
    """
    styles = custom_styles or ""
    st.markdown(
        f"""
        <div class="status status--warning fadeIn" style="{styles}">
            ⚠️ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
