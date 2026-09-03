"""Phase 1 data access.

Convenient, JSON-friendly accessors for the deterministic demo data. These
are plain Python helpers -- no API, no database, no backend changes.

Only the accessor vocabulary lives here. No simulation behavior is implemented.

"""

from .drones import DEMO_DRONES
from .incidents import DEMO_INCIDENTS
from .people import DEMO_PEOPLE
from .robots import DEMO_ROBOTS

__all__ = ["get_incidents", "get_drones", "get_robots", "get_people"]


def get_incidents() -> list[dict]:
    """Return all demo incidents as JSON-friendly dicts."""
    return [incident.to_dict() for incident in DEMO_INCIDENTS]


def get_drones() -> list[dict]:
    """Return all demo drones as JSON-friendly dicts."""
    return [drone.to_dict() for drone in DEMO_DRONES]


def get_robots() -> list[dict]:
    """Return all demo robots as JSON-friendly dicts."""
    return [robot.to_dict() for robot in DEMO_ROBOTS]


def get_people() -> list[dict]:
    """Return all demo persons as JSON-friendly dicts."""
    return [person.to_dict() for person in DEMO_PEOPLE]