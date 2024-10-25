"""
Description: Integrates Quranic audio and text data management functionality, providing a unified interface
for retrieving verse information, downloading audio files, and extracting audio metadata.
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from typing import Any

from alforqan.backend.quran_data.audio_processor import AudioDuration
from alforqan.backend.quran_data.uthmanic_hafs_parser import UthmanicHafsData
from alforqan.backend.utils.every_ayah_downloader import QuranAudioDownloader
from alforqan.constant import MAX_SURAH

import structlog

logger = structlog.get_logger(__name__)


class QuranDataManager:
    """
    Integrates QuranAudioDownloader, AudioInfoExtractor, and UthmanicHafsData
    to provide comprehensive Quranic data management functionality.
    """

    def __init__(self, quran_data_filepath: str, audio_directory: str) -> None:
        """
        Initialize QuranDataManager with required file paths.

        :param quran_data_filepath: Path to the Uthmanic Hafs JSON data file
        :param audio_directory: Base directory for storing audio files
        :raises FileNotFoundError: If Quran data file doesn't exist
        :raises PermissionError: If audio directory isn't writable
        """
        data_path = Path(quran_data_filepath)
        if not data_path.exists():
            raise FileNotFoundError(f"Required Quran data file not found at: {quran_data_filepath}")

        self.quran_data = UthmanicHafsData(quran_data_filepath)
        self.audio_downloader = QuranAudioDownloader()
        self.audio_dir = Path(audio_directory)

        try:
            self.audio_dir.mkdir(parents=True, exist_ok=True)
            # Test write permissions with a temporary file
            test_file = self.audio_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError) as e:
            logger.exception("audio_directory_access_error", directory=audio_directory, error=str(e))
            raise PermissionError(f"Cannot write to audio directory: {audio_directory}")

    def get_verses_info(self, reciter_id: int, surah_number: int, start_ayah: int, end_ayah: int) -> dict[str, list[Any]]:
        """
        Retrieve comprehensive information for a range of verses including text, audio, and metadata.

        :param reciter_id: Unique identifier for the Quran reciter
        :param surah_number: Chapter number (1-114)
        :param start_ayah: Starting verse number
        :param end_ayah: Ending verse number
        :raises ValueError: If surah or verse numbers are invalid
        :return: Dictionary containing verse information, audio paths, and durations
        """
        self._validate_verse_range(surah_number, start_ayah, end_ayah)

        reciter_config = self.audio_downloader.get_reciter_config(reciter_id)
        reciter_audio_dir = self.audio_dir / reciter_config.subfolder

        verses_data = self._process_verses_concurrently(reciter_id, surah_number, start_ayah, end_ayah, reciter_audio_dir)

        if not verses_data:
            logger.error("verses_processing_failed", surah=surah_number, verse_range=f"{start_ayah}-{end_ayah}")
            return {"verse_info": [], "verses_audio_paths": [], "verse_durations": []}

        verses_data.sort(key=lambda x: x["verse_info"]["aya_no"])

        return {
            "verse_info": [verse["verse_info"] for verse in verses_data],
            "verses_audio_paths": [verse["audio_path"] for verse in verses_data],
            "verse_durations": [verse["duration"] for verse in verses_data],
        }

    def _validate_verse_range(self, surah_number: int, start_ayah: int, end_ayah: int) -> None:
        """
        Validate surah and verse number ranges.

        :raises ValueError: If provided numbers are out of valid range
        """
        if not 1 <= surah_number <= MAX_SURAH:
            raise ValueError(f"Invalid surah number: {surah_number}")

        if start_ayah > end_ayah:
            raise ValueError(f"Start verse ({start_ayah}) cannot be greater than end verse ({end_ayah})")

    def _process_single_verse(self, reciter_id: int, surah_number: int, ayah_number: int, reciter_audio_dir: Path) -> dict[str, Any] | None:
        """
        Process a single verse: fetch text, download audio if needed, and extract metadata.
        """
        try:
            verse_info = self.quran_data.get_verse_info(surah_number, ayah_number)
            if not verse_info:
                return None

            audio_filename = f"{surah_number:03d}{ayah_number:03d}.mp3"
            audio_filepath = reciter_audio_dir / audio_filename

            if not audio_filepath.exists():
                try:
                    audio_filepath = self.audio_downloader.download_ayah(reciter_id, surah_number, ayah_number, str(reciter_audio_dir))
                except Exception as e:
                    logger.exception("audio_download_failed", surah=surah_number, ayah=ayah_number, error=str(e))
                    return None

            audio_duration = AudioDuration().get_duration(str(audio_filepath))

            return {"verse_info": verse_info, "audio_path": str(audio_filepath), "duration": audio_duration}

        except Exception as e:
            logger.exception("verse_processing_error", surah=surah_number, ayah=ayah_number, error=str(e))
            return None

    def _process_verses_concurrently(
        self, reciter_id: int, surah_number: int, start_ayah: int, end_ayah: int, reciter_audio_dir: Path
    ) -> list[dict[str, Any]]:
        """
        Process multiple verses concurrently using a thread pool.
        """
        verses_data = []
        start_time = time.time()

        with ThreadPoolExecutor() as executor:
            future_to_ayah = {
                executor.submit(self._process_single_verse, reciter_id, surah_number, ayah, reciter_audio_dir): ayah
                for ayah in range(start_ayah, end_ayah + 1)
            }

            for future in as_completed(future_to_ayah):
                if result := future.result():
                    verses_data.append(result)

        # Log only if processing took longer than expected
        processing_duration = time.time() - start_time
        if processing_duration > 5:  # Only log if processing takes more than 5 seconds
            logger.info("verses_processing_completed", verses_count=len(verses_data), duration=f"{processing_duration:.2f}s")

        return verses_data


# Usage example
if __name__ == "__main__":
    quran_data_path = "data/assets/fonts/UthmanicHafs_v2-0/UthmanicHafs_v2-0 data/hafsData_v2-0.json"
    audio_base_dir = "temp/audio"

    try:
        manager = QuranDataManager(quran_data_path, audio_base_dir)
        result = manager.get_verses_info(reciter_id=6, surah_number=1, start_ayah=1, end_ayah=7)

        logger.info("example_execution_completed", verse_count=len(result["verse_info"]), total_duration=sum(result["verse_durations"]))

    except Exception as e:
        logger.exception("example_execution_failed", error=str(e))

    ## This needed by QuranScene
    # list_verse = [item['aya_text'] for item in result["verse_info"]]
    # list_durations = result["verse_durations"]
    # list_paths = result["verses_audio_paths"]
    # verse_data = result["verse_info"][0]
    # verse_info = f"{verse_data['sura_name_en']} ({verse_data['sura_name_ar']})"
