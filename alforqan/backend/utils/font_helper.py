"""
Description:
This module provides functionality for font manipulation and text processing, including Unicode character support
verification and text cleaning operations. It wraps the fontTools library to provide a higher-level interface for
common font-related tasks.

Usage:
    font_helper = FontHelper(font_path='path/to/font.ttf')
    supported = font_helper.is_text_supported('Sample text')

Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)

License: MIT

Requirements:
    - fontTools
"""

from __future__ import annotations

from dataclasses import dataclass
import os

from fontTools.ttLib import TTFont
import structlog

# Configure logging
logger = structlog.getLogger(__name__)


@dataclass
class FontMetadata:
    """Stores metadata about the font file."""

    family_name: str
    style_name: str | None
    version: str | None
    unicode_range_count: int


class FontHelper:
    """
    A helper class for font-related operations.

    This class provides functionality for:
    - Loading and analyzing font files
    - Checking character support
    - Cleaning text based on font support
    - Extracting font metadata
    """

    def __init__(self, font_path: str):
        """
        Initialize the FontHelper with a font file.

        :param font_path: Path to the font file.
        """
        logger.info("Initializing FontHelper", font_path=font_path)
        self.font_path = font_path
        self.font: TTFont | None = None
        self.supported_unicode: set[int] = set()
        self.metadata: FontMetadata | None = None
        self._load_font()

    def _load_font(self) -> None:
        """Load the font file and initialize supported Unicode ranges."""
        if not os.path.isfile(self.font_path):
            logger.error("Font file not found", path=self.font_path)
            raise FileNotFoundError(f"Font file not found: {self.font_path}")

        try:
            logger.debug("Loading font file", path=self.font_path)
            self.font = TTFont(self.font_path)
            self._set_supported_unicode_ranges()
            self._initialize_metadata()
            logger.info("Font loaded successfully", path=self.font_path, char_count=len(self.supported_unicode))
        except Exception as e:
            logger.exception("Failed to load font", path=self.font_path, error=str(e), error_type=type(e).__name__)
            raise ValueError(f"Error loading font from {self.font_path}: {e}") from e

    def _initialize_metadata(self) -> None:
        """Initialize font metadata for quick access to common properties."""
        name_table = self.font["name"]
        self.metadata = FontMetadata(
            family_name=self._get_name_record(1) or "Unknown",
            style_name=self._get_name_record(2),
            version=self._get_name_record(5),
            unicode_range_count=len(self.supported_unicode),
        )
        logger.debug("Font metadata initialized", metadata=self.metadata)

    def _get_name_record(self, name_id: int) -> str | None:
        """Get a name record from the font's name table."""
        for record in self.font["name"].names:
            if record.nameID == name_id:
                try:
                    return record.toUnicode()
                except UnicodeDecodeError:
                    logger.warning("Failed to decode name record", name_id=name_id, platform_id=record.platformID)
        return None

    def _set_supported_unicode_ranges(self) -> None:
        """Set the supported Unicode ranges for the loaded font."""
        logger.debug("Building Unicode range support map")
        for cmap in self.font["cmap"].tables:
            if cmap.isUnicode():
                self.supported_unicode.update(cmap.cmap.keys())

        logger.info(
            "Unicode ranges loaded",
            total_chars=len(self.supported_unicode),
            sample_range=f"U+{min(self.supported_unicode):04X}-U+{max(self.supported_unicode):04X}",
        )

    def get_font_name(self) -> str | None:
        """
        Get the font name from the loaded font file.

        :return: The font name or None if the font name cannot be determined.
        """
        return self.metadata.family_name if self.metadata else None

    def is_text_supported(self, text: str) -> bool:
        """
        Check if all characters in the text are supported by the font.

        :param text: The input text to check.
        :return: True if all characters are supported, False otherwise.
        """
        return all(ord(char) in self.supported_unicode for char in text)

    def remove_unsupported_characters(self, text: str) -> str:
        """
        Remove characters not supported by the font from the input text.

        :param text: The input text to clean.
        :return: The cleaned text with only supported characters.
        """
        return "".join(char for char in text if ord(char) in self.supported_unicode)

    def process_text(self, text: str) -> str:
        """
        Process the input text, removing unsupported characters and logging warnings.

        :param text: The input text to process.
        :return: The processed text with only supported characters.
        """
        unsupported_chars = {char for char in text if ord(char) not in self.supported_unicode}

        if unsupported_chars:
            char_details = [{"char": char, "unicode": f"U+{ord(char):04X}"} for char in unsupported_chars]

            logger.warning(
                "Unsupported characters detected", text_length=len(text), unsupported_count=len(unsupported_chars), characters=char_details
            )

        cleaned_text = self.remove_unsupported_characters(text)

        logger.info(
            "Text processing completed",
            original_length=len(text),
            cleaned_length=len(cleaned_text),
            chars_removed=len(text) - len(cleaned_text),
        )

        return cleaned_text
