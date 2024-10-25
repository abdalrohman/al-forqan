"""
Description: A Python module for efficient parsing and retrieval of Quranic verses from the Uthmanic Hafs dataset,
providing a clean interface to access the official Uthmanic Hafs Quran text,
supporting verse lookups by surah and ayah numbers while maintaining the authentic text structure.
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
Datasets/Sources:
    - Uthmanic Hafs v2.0
    - Source: https://download.qurancomplex.gov.sa/resources_dev/UthmanicHafs_v2-0.zip
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path


class UthmanicHafsData:
    """Provides interface for accessing and retrieving verses from the Uthmanic Hafs Quran dataset."""

    def __init__(self, quran_file_path: str) -> None:
        """Initialize the Quran data parser.

        :param quran_file_path: Path to the Uthmanic Hafs JSON file
        :raises FileNotFoundError: If the specified file does not exist
        :raises ValueError: If the JSON file is malformed or missing required fields
        """
        if not Path(quran_file_path).exists():
            raise FileNotFoundError(f"Quran data file not found: {quran_file_path}")
        self._quran_data = self._parse_quran_json(quran_file_path)

    def _parse_quran_json(self, file_path: str) -> dict:
        """Create an optimized verse lookup structure from the Quran JSON file."""
        verse_data = defaultdict(lambda: defaultdict(dict))

        try:
            with open(file_path, encoding="utf-8") as file:
                raw_data = json.load(file)

            for verse in raw_data:
                surah_num = verse["sura_no"]
                ayah_num = verse["aya_no"]

                verse_data[surah_num][ayah_num] = {
                    "sura_name_en": verse["sura_name_en"],
                    "sura_name_ar": verse["sura_name_ar"],
                    "aya_text": verse["aya_text"],
                }

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in Quran data file")
        except KeyError as missing_field:
            raise ValueError(f"Required field missing in Quran data: {missing_field}")

        return verse_data

    def get_verse_info(self, surah_num: int, ayah_num: int) -> dict | None:
        """Retrieve complete information for a specific Quranic verse.

        :param surah_num: The surah number (1-114)
        :param ayah_num: The ayah number within the surah
        :return: Dictionary containing verse data or None if not found
        """
        try:
            verse_data = self._quran_data[surah_num][ayah_num]
            return {
                "sura_no": surah_num,
                "aya_no": ayah_num,
                "sura_name_en": verse_data["sura_name_en"],
                "sura_name_ar": verse_data["sura_name_ar"],
                "aya_text": verse_data["aya_text"],
            }
        except KeyError:
            return None


if __name__ == "__main__":
    try:
        quran_file = "../../../assets/quran_data/hafsData_v2-0.json"
        quran = UthmanicHafsData(quran_file)

        # Example: Al-Fatiha, Verse 7
        verse = quran.get_verse_info(1, 7)
        if verse:
            print(f"Surah {verse['sura_no']} - {verse['sura_name_en']} ({verse['sura_name_ar']})")
            print(f"Verse {verse['aya_no']}: {verse['aya_text']}")

        # Example: Al-Baqarah, Verse 2
        verse = quran.get_verse_info(2, 2)
        if verse:
            print(f"\nSurah {verse['sura_no']} - {verse['sura_name_en']} ({verse['sura_name_ar']})")
            print(f"Verse {verse['aya_no']}: {verse['aya_text']}")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
