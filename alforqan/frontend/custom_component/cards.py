"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

import streamlit as st


def create_iconic_card(
    icon: str, title: str, description: str, animate: bool = True, custom_styles: str | None = None, variant: str = "feature"
) -> None:
    """Create an iconic card with optional animation.

    Args:
        icon: Emoji or icon character to display
        title: Card title
        description: Card description
        animate: Whether to add fade-in animation (default: True)
        custom_styles: Optional additional CSS styles
        variant: Card variant (default: "feature")
    """
    # Apply custom styles if provided
    styles = f"style='{custom_styles}'" if custom_styles else ""

    # Add animation class if enabled
    animation_class = "fadeIn" if animate else ""

    st.markdown(
        f"""
        <div class="card card--{variant} {animation_class}" {styles}>
            <div class="icon">{icon}</div>
            <div class="content">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_iconic_card_grid(cards: list[dict], columns: int = 2, animate: bool = True, custom_styles: str | None = None) -> None:
    """Create a grid of iconic cards.

    Args:
        cards: List of dictionaries containing 'icon', 'title', and 'description'
        columns: Number of columns in the grid (default: 2)
        animate: Whether to add fade-in animation (default: True)
        custom_styles: Optional additional CSS styles
    """
    # Calculate number of rows needed
    n_cards = len(cards)
    n_rows = (n_cards + columns - 1) // columns

    # Create the grid layout
    for row in range(n_rows):
        cols = st.columns(columns)
        for col in range(columns):
            idx = row * columns + col
            if idx < n_cards:
                card = cards[idx]
                with cols[col]:
                    create_iconic_card(
                        icon=card["icon"],
                        title=card["title"],
                        description=card["description"],
                        animate=animate and idx < 6,  # Limit animations to first 6 cards
                        custom_styles=custom_styles,
                    )
