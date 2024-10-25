"""
Description: This module provides an interface for downloading Quran audio recitations from EveryAyah.com.
It supports searching and filtering reciters, downloading individual ayahs, and manages the download process with
proper error handling and retry logic.
Usage:
    downloader = QuranAudioDownloader()
    file_path = downloader.download_ayah(reciter_number=6, surah_number=1, ayah_number=1, save_dir="downloads")
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
Requirements:
    - requests
Datasets/Sources:
    - EveryAyah.com API
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
import json
from pathlib import Path
import time
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
import structlog
from urllib3.util.retry import Retry

# Configure logging
logger = structlog.getLogger(__name__)


@dataclass
class ReciterConfig:
    """Configuration details for a Quran reciter.

    :param subfolder: The directory name containing the reciter's audio files
    :param name: The full name of the reciter
    :param bitrate: Audio quality specification (e.g., '128kbps')
    :param reciter_id: Unique identifier for the reciter
    """

    subfolder: str
    name: str
    bitrate: str
    reciter_id: int | None = None

    def __str__(self) -> str:
        """Return a human-readable string representation of the reciter."""
        return f"{self.name} ({self.bitrate})"

    def get_info(self) -> dict[str, str]:
        """Return a dictionary containing the reciter's details."""
        return {
            "name": self.name,
            "quality": self.bitrate,
            "directory": self.subfolder,
            "id": str(self.reciter_id) if self.reciter_id else "Unknown",
        }


class RecitersCollection:
    """Manages the collection of available Quran reciters."""

    def __init__(self, reciters_data: dict[str, dict]):
        """
        :param reciters_data: Raw dictionary containing reciter information
        """
        self._reciter_configs = {
            int(key): ReciterConfig(**value, reciter_id=int(key)) for key, value in reciters_data.items() if key.isdigit()
        }

    def get_reciter(self, reciter_id: int) -> ReciterConfig | None:
        """Retrieve a reciter configuration by ID.

        :param reciter_id: The unique identifier of the reciter
        """
        return self._reciter_configs.get(reciter_id)

    def list_reciters(self) -> list[ReciterConfig]:
        """Return a sorted list of all available reciters."""
        return sorted(self._reciter_configs.values(), key=lambda x: x.name)

    def search_reciters(self, search_term: str) -> Iterator[ReciterConfig]:
        """Search for reciters by name.

        :param search_term: The name or partial name to search for
        """
        search_term = search_term.lower()
        for reciter in self.list_reciters():
            if search_term in reciter.reciter_name.lower():
                yield reciter

    def get_by_quality(self, quality_level: str) -> list[ReciterConfig]:
        """Filter reciters by audio quality.

        :param quality_level: The desired audio quality specification
        """
        return [reciter for reciter in self.list_reciters() if reciter.audio_quality.lower() == quality_level.lower()]


class QuranAudioDownloader:
    """Handles downloading of Quran audio files from EveryAyah.com."""

    BASE_URL = "https://www.everyayah.com/data/"
    RECITATIONS_URL = "https://www.everyayah.com/data/recitations.js"

    def __init__(self):
        self.session = self._create_session()
        self._recitations_cache: dict | None = None
        self._reciters: RecitersCollection | None = None
        self._last_request_timestamp = 0.0
        self.request_interval = 1.0  # Minimum seconds between requests

    @staticmethod
    def _create_session() -> requests.Session:
        """Create and configure an HTTP session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _apply_rate_limit(self) -> None:
        """Enforce minimum interval between API requests."""
        current_time = time.time()
        time_elapsed = current_time - self._last_request_timestamp
        if time_elapsed < self.request_interval:
            time.sleep(self.request_interval - time_elapsed)
        self._last_request_timestamp = time.time()

    def _load_recitations_data(self) -> dict:
        """Fetch and cache recitations configuration data."""
        if self._recitations_cache is None:
            self._apply_rate_limit()
            response = self.session.get(self.RECITATIONS_URL)
            response.raise_for_status()
            self._recitations_cache = json.loads(response.text.strip())
        return self._recitations_cache

    @property
    def reciters(self) -> RecitersCollection:
        """Access the collection of available reciters."""
        if self._reciters is None:
            data = self._load_recitations_data()
            self._reciters = RecitersCollection(data)
        return self._reciters

    def get_reciter_config(self, reciter_id: int) -> ReciterConfig:
        """Retrieve configuration for a specific reciter.

        :param reciter_id: The unique identifier of the reciter
        :raises ValueError: If the reciter ID is invalid
        """
        reciter = self.reciters.get_reciter(reciter_id)
        if not reciter:
            raise ValueError(f"Invalid reciter ID: {reciter_id}")
        return reciter

    def list_available_reciters(self) -> list[dict[str, str]]:
        """Return detailed information for all available reciters."""
        return [reciter.get_info() for reciter in self.reciters.list_reciters()]

    def search_reciters(self, search_term: str) -> list[dict[str, str]]:
        """Search for reciters by name and return their details.

        :param search_term: The name or partial name to search for
        """
        return [reciter.get_info() for reciter in self.reciters.search_reciters(search_term)]

    def _validate_surah_ayah(self, surah_num: int, ayah_num: int) -> None:
        """Validate surah and ayah numbers against allowed ranges.

        :param surah_num: The surah number to validate
        :param ayah_num: The ayah number to validate
        :raises ValueError: If either number is invalid
        """
        data = self._load_recitations_data()
        ayah_counts = data.get("ayahCount", [])

        if not 1 <= surah_num <= 114:
            raise ValueError("Surah number must be between 1 and 114")

        max_ayah = ayah_counts[surah_num - 1]
        if not 1 <= ayah_num <= max_ayah:
            raise ValueError(f"Ayah number must be between 1 and {max_ayah} for surah {surah_num}")

    def download_ayah(self, reciter_id: int, surah_num: int, ayah_num: int, output_dir: str | Path) -> Path:
        """Download a specific ayah recitation.

        :param reciter_id: The ID of the reciter
        :param surah_num: The surah number
        :param ayah_num: The ayah number
        :param output_dir: Directory to save the audio file
        :returns: Path to the downloaded file
        :raises ValueError: If any input parameters are invalid
        :raises requests.RequestException: If the download fails
        """
        log = logger.bind(reciter_id=reciter_id, surah_num=surah_num, ayah_num=ayah_num)

        self._validate_surah_ayah(surah_num, ayah_num)
        reciter_config = self.get_reciter_config(reciter_id)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        file_name = f"{surah_num:03d}{ayah_num:03d}.mp3"
        file_path = output_path / file_name

        download_url = urljoin(self.BASE_URL, f"{reciter_config.subfolder}/{file_name}")
        log.info("downloading_ayah", url=download_url)

        self._apply_rate_limit()
        response = self.session.get(download_url)
        response.raise_for_status()

        file_path.write_bytes(response.content)
        return file_path


# Usage
def main() -> None:
    """Demonstrate basic usage of the QuranAudioDownloader."""
    try:
        downloader = QuranAudioDownloader()

        # Example: Download first ayah of Al-Fatiha by Abdullah Basfar
        file_path = downloader.download_ayah(reciter_id=6, surah_num=1, ayah_num=1, output_dir="downloads")
        logger.info("download_successful", file_path=str(file_path))

    except Exception as error:
        logger.exception("download_failed", error=str(error))
        raise


if __name__ == "__main__":
    main()
