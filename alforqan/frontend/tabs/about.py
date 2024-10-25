"""
@author: M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
@license: MIT
"""

from __future__ import annotations

from alforqan.frontend.custom_component.cards import create_iconic_card_grid
from alforqan.frontend.custom_component.header import create_header_section
from alforqan.frontend.custom_component.step_header import create_stp_header


def display_about_section(app_config):
    """Display application information with enhanced organization and styling"""
    create_header_section(
        "Al-Forqan",
        "A powerful tool for creating beautiful video visualizations of Quranic verses",
    )
    # Features Section
    create_stp_header(1, "Key Features")
    features_section = [
        {"icon": "🎤", "title": "Multiple Reciters", "description": "Various audio qualities and recitation styles"},
        {"icon": "🎨", "title": "Custom Styling", "description": "Elegant typography and visual design options"},
        {"icon": "🎬", "title": "Flexible Output", "description": "Support for different video aspect ratios"},
        {"icon": "📊", "title": "Batch Processing", "description": "Process multiple videos efficiently"},
    ]
    create_iconic_card_grid(features_section)

    # Getting Started Section
    create_stp_header(2, "Getting Started")
    steps_section = [
        {"icon": "1️⃣", "title": "Select Reciter", "description": "Choose from our curated list of qualified reciters"},
        {"icon": "2️⃣", "title": "Choose Verses", "description": "Select the Quranic verses for visualization"},
        {"icon": "3️⃣", "title": "Customize", "description": "Adjust visual settings and styling options"},
        {"icon": "4️⃣", "title": "Generate", "description": "Process and download your visualizations"},
    ]
    create_iconic_card_grid(steps_section)

    # App Info Section
    create_stp_header(3, "App Information")
    app_info_section = [
        {"icon": "🔢", "title": "Version", "description": f"{app_config.get('package.version')}"},
        {"icon": "👤", "title": "Authors", "description": f"{app_config.get('package.authors')}"},
        {"icon": "📜", "title": "License", "description": f"{app_config.get('package.licence')}"},
        {"icon": "📝", "title": "Description", "description": f"{app_config.get('package.description')}"},
    ]
    create_iconic_card_grid(app_info_section)
