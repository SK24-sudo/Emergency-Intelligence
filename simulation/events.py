"""Phase 0 simulation event structure.

A lightweight, JSON-friendly representation of a discrete simulation
event. Each event carries the contract-level metadata needed by the
frontend and backend:

- ``event_type``: a :class:`SimulationEvent` enum member
- ``timestamp``:  when the event occurred
- ``asset_id``:   optional identifier of the drone/robot that emitted it
- ``mission_id``: optional identifier of the mission it belongs to
- ``data``:       optional free-form payload (must stay JSON-friendly)

Only the event vocabulary lives here. No database, API, or behavior.
"""

from dataclasses import dataclass, field
from typing import Any

from simulation.contract import SimulationEvent


@dataclass
class SimulationEventRecord:
    """A single simulation event.

    ``event_type`` must be a :class:`SimulationEvent` member. The other
    fields are free-form; ``data`` defaults to an empty dictionary.
    """

    event_type: SimulationEvent
    timestamp: Any
    asset_id: Any = None
    mission_id: Any = None
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.event_type, SimulationEvent):
            raise TypeError(
                f"event_type must be a SimulationEvent member, got "
                f"{self.event_type!r}"
            )

    def to_dict(self) -> dict:
        """Return a plain dictionary suitable for JSON serialization.

        ``event_type`` is represented by its string value so the result
        contains only JSON-friendly primitives. The returned ``data`` is a
        shallow copy; mutating it never mutates the event.
        """
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "asset_id": self.asset_id,
            "mission_id": self.mission_id,
            "data": dict(self.data),
        }