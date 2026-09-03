"""Deterministic drone lifecycle simulation."""

from simulation.contract import DroneState, SimulationEvent
from simulation.data.people import DEMO_PEOPLE
from simulation.events import SimulationEventRecord
from simulation.state_machine import require_valid_transition


class DroneSimulator:
    """Simulate one drone through a deterministic search mission."""

    def __init__(
        self,
        drone_id: str,
        latitude: float = 0.0,
        longitude: float = 0.0,
        battery: float = 100.0,
        base_latitude: float | None = None,
        base_longitude: float | None = None,
    ):
        self.drone_id = drone_id
        self.latitude = latitude
        self.longitude = longitude
        self.battery = max(0.0, battery)
        self.state = DroneState.AVAILABLE
        self.mission_id = None
        self.target_latitude = None
        self.target_longitude = None
        self.base_latitude = latitude if base_latitude is None else base_latitude
        self.base_longitude = longitude if base_longitude is None else base_longitude
        self.events = []
        self._event_number = 0

    def dispatch(
        self, mission_id: str, target_latitude: float, target_longitude: float
    ) -> bool:
        """Assign a mission and begin travelling to its target."""
        if (
            self.state is not DroneState.AVAILABLE
            or not isinstance(mission_id, str)
            or not mission_id
            or not self._is_coordinate(target_latitude, -90.0, 90.0)
            or not self._is_coordinate(target_longitude, -180.0, 180.0)
        ):
            return False
        self._transition(DroneState.DISPATCHED)
        self.mission_id = mission_id
        self.target_latitude = target_latitude
        self.target_longitude = target_longitude
        self._emit(
            SimulationEvent.DRONE_DISPATCHED,
            {"target_latitude": target_latitude, "target_longitude": target_longitude},
        )
        self._transition(DroneState.EN_ROUTE)
        self._emit(
            SimulationEvent.DRONE_EN_ROUTE,
            {"latitude": self.latitude, "longitude": self.longitude},
        )
        return True

    def move(self, fraction: float = 0.5) -> bool:
        """Move one deterministic interpolation step toward the active point."""
        if self.state not in (DroneState.EN_ROUTE, DroneState.RETURNING):
            return False
        if self.state is DroneState.EN_ROUTE:
            destination = (self.target_latitude, self.target_longitude)
        else:
            destination = (self.base_latitude, self.base_longitude)
        if destination[0] is None or destination[1] is None:
            return False
        if (
            not isinstance(fraction, (int, float))
            or isinstance(fraction, bool)
            or fraction <= 0.0
            or fraction > 1.0
        ):
            return False

        old_position = (self.latitude, self.longitude)
        self.latitude += (destination[0] - self.latitude) * fraction
        self.longitude += (destination[1] - self.longitude) * fraction
        if abs(destination[0] - self.latitude) <= 1e-6:
            self.latitude = destination[0]
        if abs(destination[1] - self.longitude) <= 1e-6:
            self.longitude = destination[1]
        if old_position != (self.latitude, self.longitude):
            self._consume_battery(1.0)

        if (self.latitude, self.longitude) == destination:
            if self.state is DroneState.EN_ROUTE:
                self.start_search()
            else:
                self._transition(DroneState.AVAILABLE)
                self.mission_id = None
        return True

    def move_to_target(self, fraction: float = 0.5) -> bool:
        """Alias for one movement step toward the mission target or base."""
        return self.move(fraction)

    def start_search(self) -> bool:
        """Enter the search state after reaching the mission target."""
        if self.state is not DroneState.EN_ROUTE:
            return False
        self._transition(DroneState.SEARCHING)
        self._consume_battery(0.5)
        self._emit(
            SimulationEvent.DRONE_SEARCH_STARTED,
            {"latitude": self.latitude, "longitude": self.longitude},
        )
        return True

    def detect_person(self, person_id: str | None = None) -> bool:
        """Detect one deterministic demo person during a search."""
        if self.state is not DroneState.SEARCHING:
            return False
        if person_id is None:
            person = DEMO_PEOPLE[0]
        else:
            person = next(
                (candidate for candidate in DEMO_PEOPLE if candidate.id == person_id),
                None,
            )
            if person is None:
                return False
        person_data = person.to_dict()
        person_data["person_id"] = person.id
        self._consume_battery(0.5)
        self._transition(DroneState.PERSON_FOUND)
        self._emit(SimulationEvent.PERSON_DETECTED, person_data)
        self._emit(
            SimulationEvent.PERSON_LOCATION_IDENTIFIED,
            {
                "person_id": person.id,
                "latitude": person.latitude,
                "longitude": person.longitude,
            },
        )
        return True

    def return_to_base(self) -> bool:
        """Begin deterministic travel back to the drone's base."""
        if self.state is not DroneState.PERSON_FOUND:
            return False
        self._transition(DroneState.RETURNING)
        return True

    def to_dict(self) -> dict:
        """Return the current simulator state as JSON-friendly primitives."""
        return {
            "drone_id": self.drone_id,
            "state": self.state.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "battery": self.battery,
            "mission_id": self.mission_id,
            "target_latitude": self.target_latitude,
            "target_longitude": self.target_longitude,
            "base_latitude": self.base_latitude,
            "base_longitude": self.base_longitude,
        }

    def _transition(self, requested: DroneState) -> None:
        require_valid_transition(self.state, requested)
        self.state = requested

    def _emit(self, event_type: SimulationEvent, data: dict) -> None:
        self._event_number += 1
        self.events.append(
            SimulationEventRecord(
                event_type=event_type,
                timestamp=self._event_number,
                asset_id=self.drone_id,
                mission_id=self.mission_id,
                data=data,
            )
        )

    def _consume_battery(self, amount: float) -> None:
        self.battery = max(0.0, self.battery - amount)

    @staticmethod
    def _is_coordinate(value, minimum, maximum):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value == value
            and minimum <= value <= maximum
        )