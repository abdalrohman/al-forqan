from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DirectionInfo:
    """Information about a direction vector."""

    name: str
    vector: np.ndarray
    description: str


class ManimDirections:
    """Manager class for Manim direction vectors."""

    def __init__(self):
        # Initialize all direction vectors
        self.ORIGIN = np.array((0.0, 0.0, 0.0))
        self.UP = np.array((0.0, 1.0, 0.0))
        self.DOWN = np.array((0.0, -1.0, 0.0))
        self.RIGHT = np.array((1.0, 0.0, 0.0))
        self.LEFT = np.array((-1.0, 0.0, 0.0))
        self.IN = np.array((0.0, 0.0, -1.0))
        self.OUT = np.array((0.0, 0.0, 1.0))
        self.UL = self.UP + self.LEFT
        self.UR = self.UP + self.RIGHT
        self.DL = self.DOWN + self.LEFT
        self.DR = self.DOWN + self.RIGHT

        # Create direction information map
        self.direction_map: dict[str, DirectionInfo] = {
            "ORIGIN": DirectionInfo(
                name="Origin",
                vector=self.ORIGIN,
                description="Center of the coordinate system (0, 0, 0)",
            ),
            "UP": DirectionInfo(
                name="Up",
                vector=self.UP,
                description="Upward direction along Y-axis",
            ),
            "DOWN": DirectionInfo(
                name="Down",
                vector=self.DOWN,
                description="Downward direction along Y-axis",
            ),
            "RIGHT": DirectionInfo(
                name="Right",
                vector=self.RIGHT,
                description="Rightward direction along X-axis",
            ),
            "LEFT": DirectionInfo(
                name="Left",
                vector=self.LEFT,
                description="Leftward direction along X-axis",
            ),
            "IN": DirectionInfo(
                name="In",
                vector=self.IN,
                description="Inward direction along Z-axis (toward screen)",
            ),
            "OUT": DirectionInfo(
                name="Out",
                vector=self.OUT,
                description="Outward direction along Z-axis (away from screen)",
            ),
            "UP_LEFT": DirectionInfo(
                name="Up-Left",
                vector=self.UL,
                description="Diagonal direction combining up and left",
            ),
            "UP_RIGHT": DirectionInfo(
                name="Up-Right",
                vector=self.UR,
                description="Diagonal direction combining up and right",
            ),
            "DOWN_LEFT": DirectionInfo(
                name="Down-Left",
                vector=self.DL,
                description="Diagonal direction combining down and left",
            ),
            "DOWN_RIGHT": DirectionInfo(
                name="Down-Right",
                vector=self.DR,
                description="Diagonal direction combining down and right",
            ),
        }

    def get_direction_vector(self, direction_name: str) -> np.ndarray:
        """Get the vector for a given direction name."""
        return self.direction_map[direction_name.upper()].vector

    def get_direction_info(self, direction_name: str) -> DirectionInfo:
        """Get the complete information for a given direction name."""
        return self.direction_map[direction_name.upper()]

    def get_all_directions(self) -> list[DirectionInfo]:
        """Get a list of all direction information."""
        return list(self.direction_map.values())

    def get_streamlit_options(self) -> list[tuple[str, str]]:
        """Get direction options formatted for Streamlit selectbox."""
        return [(name, f"{info.name} - {info.description}") for name, info in self.direction_map.items()]
