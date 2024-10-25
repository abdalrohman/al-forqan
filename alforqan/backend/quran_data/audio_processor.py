"""
Description: A comprehensive audio processing module that provides functionality for audio file manipulation,
including duration extraction, normalization, silence removal, and file merging.
The module handles various audio formats through the mutagen library with fallback support for wave format.
Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)
License: MIT
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
import os
from pathlib import Path
import tempfile
import wave

import mutagen
from pydub import AudioSegment
from pydub.silence import detect_leading_silence

__all__ = ["AudioProcessor", "AudioDuration"]


class AudioProcessorError(Exception):
    """Base exception for audio processing validation errors."""

    pass


class AudioDuration:
    """Handles audio duration extraction and formatting."""

    @staticmethod
    def get_duration(file_path: str | Path) -> float:
        """Extract duration of an audio file in seconds.

        :param file_path: Path to the audio file
        :raises ValueError: If file doesn't exist or duration cannot be determined
        """
        file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"File not found: {file_path}")

        try:
            audio = mutagen.File(str(file_path))
            if audio is not None and hasattr(audio.info, "length"):
                return audio.info.length

            with wave.open(str(file_path), "rb") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)
        except Exception as e:
            raise ValueError(f"Failed to extract duration: {e}")

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Convert duration from seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class AudioProcessor:
    """Audio processing class with support for normalization, silence removal, and file merging."""

    def __init__(
        self,
        silence_thresh: int = -50,
        min_silence_duration: int = 70,
        fade_len: int = 15,
        padding_len: int = 20,
    ):
        """Initialize processor with audio manipulation parameters.

        :param silence_thresh: Silence detection threshold in dB (-100 to 0)
        :param min_silence_duration: Minimum silence duration to process in ms
        :param fade_len: Duration of fade effects in ms
        :param padding_len: Silence padding duration in ms
        :raises AudioProcessorError: If parameters are invalid
        """
        if not -100 <= silence_thresh <= 0:
            raise AudioProcessorError(f"Invalid silence threshold: {silence_thresh}. Must be between -100 and 0 dB")

        if min_silence_duration <= 0:
            raise AudioProcessorError(f"Invalid silence duration: {min_silence_duration}. Must be positive")

        if padding_len * 2 >= min_silence_duration:
            raise AudioProcessorError(f"Invalid padding length: {padding_len}. Must be less than {min_silence_duration // 2}ms")

        if fade_len >= min_silence_duration / 4:
            raise AudioProcessorError(f"Invalid fade length: {fade_len}. Must be less than {min_silence_duration // 4}ms")

        self.silence_thresh = silence_thresh
        self.min_silence_duration = min_silence_duration
        self.fade_len = fade_len
        self.padding_len = padding_len
        self.temp_dir = tempfile.mkdtemp()
        self.duration_handler = AudioDuration()

    def normalize_audio(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        target_dbfs: float = -17.0,
    ) -> str:
        """Normalize audio volume to target dBFS level."""
        output_path = output_path or self._create_temp_path("normalized.mp3")
        audio = AudioSegment.from_file(str(input_path))
        normalized_audio = audio.apply_gain(target_dbfs - audio.dBFS)
        normalized_audio.export(str(output_path), format="mp3")
        return str(output_path)

    @classmethod
    def create_with_preset(cls, preset: str = "default") -> AudioProcessor:
        """Create processor instance with predefined settings.

        :param preset: Configuration preset name ('default', 'conservative', 'aggressive')
        :raises ValueError: If preset name is invalid
        """
        presets = {
            "default": {"silence_thresh": -50, "min_silence_duration": 300, "fade_len": 20, "padding_len": 40},
            "conservative": {"silence_thresh": -60, "min_silence_duration": 500, "fade_len": 30, "padding_len": 100},
            "aggressive": {"silence_thresh": -40, "min_silence_duration": 200, "fade_len": 10, "padding_len": 25},
        }

        if preset not in presets:
            raise ValueError(f"Invalid preset: {preset}. Available: {', '.join(presets.keys())}")

        return cls(**presets[preset])

    def preprocess_audio(self, input_path: str | Path, output_path: str | Path | None = None) -> dict[str, float]:
        """Process audio by removing silence and adding fades."""
        output_path = output_path or self._create_temp_path("preprocessed.mp3")
        audio = AudioSegment.from_file(str(input_path))

        audio = (
            audio[detect_leading_silence(audio, silence_threshold=self.silence_thresh) + self.padding_len :]
            .strip_silence(silence_thresh=self.silence_thresh, silence_len=self.min_silence_duration, padding=self.padding_len)
            .fade_in(self.fade_len)
            .fade_out(self.fade_len)
        )

        audio.export(str(output_path), format="mp3")
        duration = self.duration_handler.get_duration(output_path)
        return {"path": str(output_path), "duration": duration}

    def merge_audio_files(
        self,
        file_paths: list[str | Path] | Iterator[Path],
        output_path: str | Path,
        crossfade: int = 500,
    ) -> dict[str, str | float | list[dict]]:
        """Merge multiple audio files with crossfade effect and track duration changes.

        :param file_paths: Audio files to merge
        :param output_path: Path for merged output
        :param crossfade: Crossfade duration in ms
        :raises TypeError: If file_paths has invalid type
        :raises ValueError: If no input files provided
        :returns: Dictionary containing output path, duration, formatted duration, and list of duration changes
        """
        if isinstance(file_paths, Iterator | Generator):
            file_paths = list(file_paths)

        if not isinstance(file_paths, list):
            raise TypeError("file_paths must be a list or iterator of paths")

        if not file_paths:
            raise ValueError("No input files provided")

        merged = AudioSegment.empty()
        duration_changes = []
        total_duration_ms = 0
        cumulative_crossfade = 0

        for i, path in enumerate(file_paths):
            current_audio = AudioSegment.from_file(str(path))
            original_duration = len(current_audio)  # Duration in milliseconds

            if len(merged) > 0:
                # Calculate the actual contribution to final duration
                # Each file after the first one contributes: its full length - crossfade
                effective_duration = original_duration - crossfade
                cumulative_crossfade += crossfade
            else:
                # First file contributes its full length
                effective_duration = original_duration

            total_duration_ms += effective_duration

            duration_changes.append(
                {
                    "file": str(path),
                    "original_duration_ms": original_duration,
                    "effective_duration_ms": effective_duration,
                    "difference_ms": effective_duration - original_duration,
                    "difference_seconds": (effective_duration - original_duration) / 1000,
                }
            )

            # Perform the actual merge
            merged = merged.append(current_audio, crossfade=crossfade) if len(merged) > 0 else current_audio

        merged.export(str(output_path), format="mp3")
        final_duration = self.duration_handler.get_duration(output_path)

        # Add verification data
        return {
            "output_path": str(output_path),
            "duration": final_duration,
            "formatted_duration": self.duration_handler.format_duration(final_duration),
            "calculated_duration_ms": total_duration_ms,
            "calculated_duration_seconds": total_duration_ms / 1000,
            "total_crossfade_duration_ms": cumulative_crossfade,
            "duration_changes": duration_changes,
        }

    def _create_temp_path(self, filename: str) -> str:
        """Generate path for temporary file."""
        return os.path.join(self.temp_dir, filename)

    def cleanup(self) -> None:
        """Remove temporary files and directory."""
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


def compare_durations(input_path: Path, output_path: Path) -> None:
    """Compare durations of input and output files."""
    duration_handler = AudioDuration()
    try:
        input_duration = duration_handler.get_duration(input_path)
        output_duration = duration_handler.get_duration(output_path)

        print("\nDuration Comparison:")
        print(f"Input:  {duration_handler.format_duration(input_duration)}")
        print(f"Output: {duration_handler.format_duration(output_duration)}")
        print(f"Difference: {abs(output_duration - input_duration):.2f} seconds")

    except ValueError as e:
        print(f"Duration comparison failed: {e}")


# Usage
if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent.parent.parent
    input_dir = base_dir / "temp/audio/Abdullah_Basfar_192kbps"
    input_file = input_dir / "001001.mp3"
    output_dir = base_dir / "temp/normalize"
    normalized_out = output_dir / "normalized_audio.mp3"
    merged_output = output_dir / "merged_final.mp3"
    with AudioProcessor() as audio_processor:
        audio_processor.create_with_preset("aggressive").preprocess_audio(input_file, normalized_out)
        # audio_processor.merge_audio_files(
        #     input_dir.iterdir(),
        #     merged_output,
        # )

    compare_durations(input_file, normalized_out)
