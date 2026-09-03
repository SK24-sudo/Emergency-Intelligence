"""Phase 1 robot demo data.

Deterministic, JSON-friendly demo robots used to drive the simulation.

All values are hard-coded (fixed coordinates, no randomness). Status uses
the :class:`RobotState` contract enum and defaults to ``AVAILABLE``. This
is data only; no robot movement behavior lives here.
"""

from dataclasses import dataclass
from typing import Optional

from simulation.contract import RobotState


@dataclass(frozen=True)
class Robot:
    """A single JSON-friendly robot with fixed values."""

    id: str
    name: str
    status: RobotState = RobotState.AVAILABLE
    latitude: float = 0.0
    longitude: float = 0.0
    battery: float = 100.0
    current_mission: Optional[str] = None

    def to_dict(self) -> dict:
        """Return a plain dictionary suitable for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "battery": self.battery,
            "current_mission": self.current_mission,
        }


# Fixed, deterministic demo robots. Do not add randomness here.
DEMO_ROBOTS = [
    Robot(
        id="ROBOT-01",
        name="NR-01",
        status=RobotState.AVAILABLE,
        latitude=18.5204,
        longitude=73.8567,
        battery=100.0,
        current_mission=None,
    ),
    Robot(
        id="ROBOT-02",
        name="NR-02",
        status=RobotState.AVAILABLE,
        latitude=19.9975,
        longitude=73.7898,
        battery=90.0,
        current_mission=None,
    ),
]