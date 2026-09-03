"""Phase 0 simulation contract.

Canonical state and event enums shared by the simulation, backend, and
frontend. This module defines the vocabulary only; no simulation behavior
is implemented here.
"""

from enum import StrEnum


class DroneState(StrEnum):
    """Lifecycle states of a search drone."""

    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    SEARCHING = "searching"
    PERSON_FOUND = "person_found"
    RETURNING = "returning"


class RobotState(StrEnum):
    """Lifecycle states of a rescue robot."""

    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ARRIVED = "arrived"
    ASSISTING = "assisting"
    RESCUE_COMPLETE = "rescue_complete"


class MissionState(StrEnum):
    """Lifecycle states of an overall rescue mission."""

    CREATED = "created"
    DISPATCHED = "dispatched"
    ACTIVE = "active"
    COMPLETED = "completed"


class SimulationEvent(StrEnum):
    """Discrete events emitted by the simulation as it progresses."""

    DRONE_DISPATCHED = "drone_dispatched"
    DRONE_EN_ROUTE = "drone_en_route"
    DRONE_SEARCH_STARTED = "drone_search_started"
    PERSON_DETECTED = "person_detected"
    PERSON_LOCATION_IDENTIFIED = "person_location_identified"
    ROBOT_DISPATCHED = "robot_dispatched"
    ROBOT_ARRIVED = "robot_arrived"
    RESCUE_STARTED = "rescue_started"
    RESCUE_COMPLETED = "rescue_completed"