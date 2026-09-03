"""Phase 1 incident demo data.

Deterministic, JSON-friendly demo incidents used to drive the simulation.

All values are hard-coded (fixed coordinates, no randomness, no external
API). This is data only; no drone or robot simulation behavior lives here.
"""

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Incident severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Priority(StrEnum):
    """Incident priority tiers."""

    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


@dataclass(frozen=True)
class Incident:
    """A single JSON-friendly incident with fixed values."""

    id: str
    name: str
    type: str
    severity: Severity
    priority: Priority
    latitude: float
    longitude: float
    description: str

    def to_dict(self) -> dict:
        """Return a plain dictionary suitable for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "severity": self.severity.value,
            "priority": self.priority.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
        }


# Fixed, deterministic demo incidents. Do not add randomness here.
DEMO_INCIDENTS = [
    Incident(
        id="inc-pune-flood",
        name="Pune Flood",
        type="flood",
        severity=Severity.CRITICAL,
        priority=Priority.P1,
        latitude=18.5204,
        longitude=73.8567,
        description="Severe flooding across low-lying areas of Pune.",
    ),
    Incident(
        id="inc-nashik-fire",
        name="Nashik Fire",
        type="fire",
        severity=Severity.HIGH,
        priority=Priority.P2,
        latitude=19.9975,
        longitude=73.7898,
        description="Large fire reported in a residential zone of Nashik.",
    ),
    Incident(
        id="inc-nagpur-accident",
        name="Nagpur Accident",
        type="accident",
        severity=Severity.MEDIUM,
        priority=Priority.P3,
        latitude=21.1458,
        longitude=79.0882,
        description="Multi-vehicle accident on a highway near Nagpur.",
    ),
]