"""
Description: This module provides functionality to extract duration and timing information from audio files.
Supports various audio formats through mutagen library with fallback to wave format.
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
"""

from __future__ import annotations

from contextlib import contextmanager
import os
import wave

import mutagen
import structlog

# Configure logger
logger = structlog.get_logger(__name__)
logger = logger.bind(module="AudioInfoExtractor")


class AudioInfoExtractor:
    """Extract timing and duration information from audio files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.audio = None
        logger.debug("initialized_extractor", file_path=file_path)

    @contextmanager
    def open_audio_file(self):
        """Context manager to handle opening and closing of audio files."""
        logger.debug("opening_audio_file", file_path=self.file_path)

        if not os.path.exists(self.file_path):
            logger.error("file_not_found", file_path=self.file_path)
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")

        try:
            self.audio = mutagen.File(self.file_path)
            if self.audio is None:
                logger.debug("attempting_wave_format", file_path=self.file_path)
                with wave.open(self.file_path, "rb") as wav_file:
                    yield wav_file
            else:
                logger.debug(
                    "using_mutagen_format",
                    file_path=self.file_path,
                    format=self.audio.mime[0] if hasattr(self.audio, "mime") else "unknown",
                )
                yield self.audio
        except Exception as e:
            logger.exceptions("file_open_error", file_path=self.file_path, error=str(e), error_type=type(e).__name__)
            raise
        finally:
            # We don't need to explicitly close Mutagen objects
            logger.debug("closing_audio_file", file_path=self.file_path)
            pass

    def get_audio_duration(self) -> float:
        """Get the duration of the audio file."""
        logger.debug("getting_audio_duration", file_path=self.file_path)
        with self.open_audio_file() as audio:
            if isinstance(audio, wave.Wave_read):
                frames = audio.getnframes()
                rate = audio.getframerate()
                duration = frames / float(rate)
                logger.debug("got_wave_duration", frames=frames, rate=rate, duration=duration)
                return duration
            elif hasattr(audio, "info") and hasattr(audio.info, "length"):
                duration = audio.info.length
                logger.debug("got_mutagen_duration", duration=duration)
                return duration
            else:
                logger.error("unsupported_format", file_path=self.file_path)
                raise ValueError("Unsupported audio format or unable to determine duration")

    def format_duration(self, duration: float) -> str:
        """Format the duration into HH:MM:SS."""
        minutes, seconds = divmod(int(duration), 60)
        hours, minutes = divmod(minutes, 60)
        formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        logger.debug("formatted_duration", raw_duration=duration, formatted_duration=formatted)
        return formatted

    def get_audio_info(self) -> dict:
        """Get time information about the audio file."""
        logger.debug("getting_audio_info", file_path=self.file_path)
        try:
            duration = self.get_audio_duration()
            info = {"duration": duration, "formatted_duration": self.format_duration(duration)}
            logger.debug("audio_info_extracted", **info)
            return info
        except Exception as e:
            error_info = {"error": str(e)}
            logger.exceptions("audio_info_extraction_failed", error=str(e), error_type=type(e).__name__)
            return error_info


if __name__ == "__main__":
    file_path = "temp/001001.mp3"
    logger.info("starting_extraction", file_path=file_path)

    extractor = AudioInfoExtractor(file_path)
    info = extractor.get_audio_info()

    if "error" in info:
        logger.error("main_execution_error", error=info["error"])
        print(f"Error: {info['error']}")
    else:
        logger.info("main_execution_success", formatted_duration=info["formatted_duration"], total_seconds=info["duration"])
        print(f"Audio Duration: {info['formatted_duration']}")
        print(f"Total Seconds: {info['duration']:.2f}")
