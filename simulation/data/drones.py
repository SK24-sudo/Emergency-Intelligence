"""Phase 1 drone demo data.

Deterministic, JSON-friendly demo drones used to drive the simulation.

All values are hard-coded (fixed coordinates, no randomness). Status uses
the :class:`DroneState` contract enum and defaults to ``AVAILABLE``. This
is data only; no drone movement behavior lives here.
"""

from dataclasses import dataclass
from typing import Optional

from simulation.contract import DroneState


@dataclass(frozen=True)
class Drone:
    """A single JSON-friendly drone with fixed values."""

    id: str
    name: str
    status: DroneState = DroneState.AVAILABLE
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


# Fixed, deterministic demo drones. Do not add randomness here.
DEMO_DRONES = [
    Drone(
        id="DRONE-01",
        name="ND-01",
        status=DroneState.AVAILABLE,
        latitude=18.5204,
        longitude=73.8567,
        battery=100.0,
        current_mission=None,
    ),
    Drone(
        id="DRONE-02",
        name="ND-02",
        status=DroneState.AVAILABLE,
        latitude=19.9975,
        longitude=73.7898,
        battery=86.5,
        current_mission=None,
    ),
    Drone(
        id="DRONE-03",
        name="ND-03",
        status=DroneState.AVAILABLE,
        latitude=21.1458,
        longitude=79.0882,
        battery=92.0,
        current_mission=None,
    ),
]