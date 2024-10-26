from __future__ import annotations


def sanitize_name(name: str) -> str:
    """Sanitize the reciter name by removing parentheses and special characters"""
    # Remove everything in parentheses and special characters
    import re

    # Remove parentheses and their contents
    name = re.sub(r"\s*\([^)]*\)", "", name)
    # Replace special characters with underscore
    name = re.sub(r"[^\w\s-]", "_", name)
    # Replace multiple spaces with single underscore
    name = re.sub(r"\s+", "_", name)
    # Remove leading/trailing underscores
    return name.strip("_").lower()
