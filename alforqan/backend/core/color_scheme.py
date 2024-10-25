"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from enum import Enum

__all__ = ["ColorScheme", "COLOR_SCHEMES"]


class ColorScheme(Enum):
    """Enumeration of available Alforqan color schemes."""

    DESERT_SUNSET = "desert_sunset"
    MOSQUE_AZURE = "mosque_azure"
    GOLDEN_DOME = "golden_dome"
    ARABESQUE = "arabesque"
    PRAYER_NIGHT = "prayer_night"
    CALLIGRAPHY = "calligraphy"
    PERSIAN_GARDEN = "persian_garden"
    ANDALUSIAN = "andalusian"
    DAMASCUS_MORNING = "damascus_morning"
    MEDINA_EVENING = "medina_evening"
    OTTOMAN_ROYAL = "ottoman_royal"
    PROPHETIC_GREEN = "prophetic_green"
    KAABA_BLACK = "kaaba_black"
    ISLAMIC_MANUSCRIPT = "islamic_manuscript"


# The last color used for font and the rest used in background
COLOR_SCHEMES = {
    ColorScheme.DESERT_SUNSET: ["#B76E22", "#C69749", "#E3C770", "#EAD7BB", "#FFFFFF"],
    ColorScheme.MOSQUE_AZURE: ["#006C67", "#00A9A5", "#90E0EF", "#CAF0F8", "#FFFFFF"],
    ColorScheme.GOLDEN_DOME: ["#916A3D", "#C4A962", "#DAC585", "#F0E6C8", "#FFFFFF"],
    ColorScheme.ARABESQUE: ["#1F4E5F", "#5B8A72", "#BAC7A7", "#E5E4CC", "#FFFFFF"],
    ColorScheme.PRAYER_NIGHT: ["#0A2342", "#2C4A7F", "#537EC5", "#89A7E0", "#FFFFFF"],
    ColorScheme.CALLIGRAPHY: ["#2C3E50", "#34495E", "#5D6D7E", "#85929E", "#FFFFFF"],
    ColorScheme.PERSIAN_GARDEN: ["#2A6041", "#4B8063", "#89B6A5", "#C4E3D7", "#FFFFFF"],
    ColorScheme.ANDALUSIAN: ["#7B4B94", "#9B6B9E", "#BB8FA9", "#DDC4DD", "#FFFFFF"],
    ColorScheme.DAMASCUS_MORNING: ["#D68438", "#E4A853", "#F2CC8F", "#FAE6BE", "#FFFFFF"],
    ColorScheme.MEDINA_EVENING: ["#553772", "#674EA7", "#9B8ABA", "#C3B7D9", "#FFFFFF"],
    ColorScheme.OTTOMAN_ROYAL: ["#8C1C13", "#BF4342", "#E7D7C1", "#F4E6CC", "#FFFFFF"],
    ColorScheme.PROPHETIC_GREEN: ["#0B4619", "#1B6B3C", "#4E9B5E", "#8FBC94", "#FFFFFF"],
    ColorScheme.KAABA_BLACK: ["#191919", "#2D2D2D", "#4D4D4D", "#808080", "#FFFFFF"],
    ColorScheme.ISLAMIC_MANUSCRIPT: ["#8B4513", "#BC7642", "#DEB887", "#F5DEB3", "#FFFFFF"],
}

## For test the color schemes
# class ColorSchemeTest(Scene):
#     def construct(self):
#         # Configuration for layout
#         scheme_height = 0.4  # Height of each color swatch
#         scheme_width = 0.8  # Width of each color swatch
#         h_spacing = 0.2  # Horizontal spacing between schemes
#         v_spacing = 0.6  # Vertical spacing between schemes
#         n_cols = 3  # Number of columns in the grid
#
#         # Create title
#         title = Text("Alforqan Color Schemes", font_size=36)
#         title.to_edge(UP, buff=0.5)
#         self.add(title)
#
#         # Calculate layout
#         schemes = list(COLOR_SCHEMES.items())
#         n_rows = (len(schemes) + n_cols - 1) // n_cols
#
#         # Calculate total width and height needed for one scheme
#         scheme_total_width = scheme_width * 5  # 5 colors per scheme
#         total_width = scheme_total_width * n_cols + h_spacing * (n_cols - 1)
#
#         # Calculate starting position to center everything
#         start_x = -(total_width / 2)
#         start_y = 2.5  # Starting y position below title
#
#         # Create all schemes
#         for i, (scheme, colors) in enumerate(schemes):
#             # Calculate grid position
#             row = i // n_cols
#             col = i % n_cols
#
#             # Calculate position for this scheme
#             x_pos = start_x + col * (scheme_total_width + h_spacing)
#             y_pos = start_y - row * (scheme_height + v_spacing)
#
#             # Create scheme name with smaller font size and positioned closer to swatches
#             name = Text(
#                 scheme.value.replace("_", " ").title(),
#                 font_size=14,
#             )
#             name.move_to(
#                 [
#                     x_pos + scheme_total_width / 2,  # Center horizontally
#                     y_pos + scheme_height / 2 + 0.15,  # Position closer to swatches
#                     0,
#                 ]
#             )
#
#             # Create color swatches
#             swatches = VGroup()
#             for j, color in enumerate(colors):
#                 swatch = Rectangle(
#                     height=scheme_height,
#                     width=scheme_width,
#                     fill_color=color,
#                     fill_opacity=1,
#                     stroke_width=1,
#                     stroke_color="#333333",
#                 )
#                 swatch.move_to([x_pos + j * scheme_width, y_pos, 0])
#                 swatches.add(swatch)
#
#             self.add(name, swatches)
