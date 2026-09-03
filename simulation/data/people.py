"""Phase 1 person demo data.

Deterministic, JSON-friendly demo persons used to drive the simulation.

Confidence is a number between 0 and 1. Distress level is expressed with
the coarsely-defined :class:`Distress` values. No medical certainty is
claimed anywhere here; ``description`` values are strictly observational.
This is data only; no camera detection behavior lives here.
"""

from dataclasses import dataclass
from enum import StrEnum


class Distress(StrEnum):
    """Coarse distress level for a detected person."""

    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True, init=False)
class Person:
    """A single JSON-friendly detected person with fixed values."""

    id: str
    latitude: float
    longitude: float
    confidence: float
    distress: Distress
    description: str

    def __init__(
        self,
        id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        confidence: float | None = None,
        distress: Distress | str | None = None,
        description: str = "",
        *,
        person_id: str | None = None,
    ):
        resolved_id = person_id if person_id is not None else id
        if not isinstance(resolved_id, str) or not resolved_id:
            raise ValueError("person_id must be a non-empty string")
        if not self._is_valid_coordinate(latitude, -90.0, 90.0):
            raise ValueError("latitude must be between -90 and 90")
        if not self._is_valid_coordinate(longitude, -180.0, 180.0):
            raise ValueError("longitude must be between -180 and 180")
        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or confidence != confidence
            or not 0.0 <= confidence <= 1.0
        ):
            raise ValueError("confidence must be between 0 and 1")
        try:
            resolved_distress = Distress(distress)
        except (TypeError, ValueError):
            raise ValueError("distress must be a valid Distress value") from None

        object.__setattr__(self, "id", resolved_id)
        object.__setattr__(self, "latitude", latitude)
        object.__setattr__(self, "longitude", longitude)
        object.__setattr__(self, "confidence", float(confidence))
        object.__setattr__(self, "distress", resolved_distress)
        object.__setattr__(self, "description", description)

    @staticmethod
    def _is_valid_coordinate(value, minimum, maximum):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value == value
            and minimum <= value <= maximum
        )

    @property
    def person_id(self) -> str:
        """Return the Phase 4 name for the existing person identifier."""
        return self.id

    def to_dict(self) -> dict:
        """Return a plain dictionary suitable for JSON serialization."""
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "confidence": self.confidence,
            "distress": self.distress.value,
            "description": self.description,
        }


# Fixed, deterministic demo persons for the Pune flood scenario. Do not
# add randomness here. Descriptions are factual; no medical claims.
DEMO_PEOPLE = [
    Person(
        id="PERSON-001",
        latitude=18.5211,
        longitude=73.8572,
        confidence=0.95,
        distress=Distress.HIGH,
        description="Person spotted on a rooftop in the flooded low-lying "
        "area of Pune.",
    ),
    Person(
        id="PERSON-002",
        latitude=18.5198,
        longitude=73.8559,
        confidence=0.88,
        distress=Distress.HIGH,
        description="Person waved at the drone near a partially submerged "
        "building in Pune.",
    ),
    Person(
        id="PERSON-003",
        latitude=18.5216,
        longitude=73.8581,
        confidence=0.82,
        distress=Distress.HIGH,
        description="Person standing beside an inflatable boat in the "
        "flooded area of Pune.",
    ),
]