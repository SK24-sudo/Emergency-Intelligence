"""Deterministic simulated camera feed and person detection."""

import copy

from simulation.contract import SimulationEvent
from simulation.data.people import DEMO_PEOPLE
from simulation.events import SimulationEventRecord


class CameraSimulator:
    """Simulate one camera attached to a drone."""

    OFF = "off"
    ACTIVE = "active"

    def __init__(self, camera_id: str, drone_id: str):
        self.camera_id = camera_id
        self.drone_id = drone_id
        self.status = self.OFF
        self.current_frame = None
        self.events = []
        self._frame_number = 0
        self._event_number = 0

    def activate(self) -> bool:
        """Activate the camera if it is currently off."""
        if self.status != self.OFF:
            return False
        self.status = self.ACTIVE
        return True

    def deactivate(self) -> bool:
        """Deactivate the camera if it is currently active."""
        if self.status != self.ACTIVE:
            return False
        self.status = self.OFF
        return True

    def is_active(self) -> bool:
        """Return whether the camera can produce feed data."""
        return self.status == self.ACTIVE

    def capture_frame(self) -> dict | None:
        """Return the next deterministic simulated frame when active."""
        if not self.is_active():
            return None
        self._frame_number += 1
        self.current_frame = {
            "camera_id": self.camera_id,
            "drone_id": self.drone_id,
            "frame_id": self._frame_number,
            "timestamp": f"simulated-{self._frame_number}",
            "simulated": True,
        }
        return copy.deepcopy(self.current_frame)

    def detect_person(self, person_id: str | None = None) -> dict | None:
        """Return a deterministic detection from the existing demo people."""
        if not self.is_active():
            return None
        if person_id is None:
            person = DEMO_PEOPLE[0]
        else:
            person = next(
                (candidate for candidate in DEMO_PEOPLE if candidate.id == person_id),
                None,
            )
            if person is None:
                return None
        frame = self.capture_frame()
        detection = person.to_dict()
        detection["person_id"] = person.id
        detection["frame_id"] = frame["frame_id"]
        detection["camera_id"] = self.camera_id
        detection["drone_id"] = self.drone_id
        self._emit(SimulationEvent.PERSON_DETECTED, detection)
        self._emit(
            SimulationEvent.PERSON_LOCATION_IDENTIFIED,
            {
                "person_id": person.id,
                "latitude": person.latitude,
                "longitude": person.longitude,
                "camera_id": self.camera_id,
                "drone_id": self.drone_id,
            },
        )
        return copy.deepcopy(detection)

    def to_dict(self) -> dict:
        """Return the camera state and latest frame as JSON-friendly data."""
        return {
            "camera_id": self.camera_id,
            "drone_id": self.drone_id,
            "status": self.status,
            "current_frame": copy.deepcopy(self.current_frame),
        }

    def _emit(self, event_type: SimulationEvent, data: dict) -> None:
        self._event_number += 1
        self.events.append(
            SimulationEventRecord(
                event_type=event_type,
                timestamp=self._event_number,
                asset_id=self.drone_id,
                data=data,
            )
        )