"""Deterministic robot rescue simulation."""

from simulation.contract import RobotState, SimulationEvent
from simulation.events import SimulationEventRecord
from simulation.state_machine import require_valid_transition


class RobotSimulator:
    """Simulate one rescue robot through a person-location mission."""

    def __init__(
        self,
        robot_id: str,
        latitude: float = 0.0,
        longitude: float = 0.0,
        battery: float = 100.0,
        base_latitude: float | None = None,
        base_longitude: float | None = None,
    ):
        self.robot_id = robot_id
        self.latitude = latitude
        self.longitude = longitude
        self.battery = max(0.0, battery)
        self.state = RobotState.AVAILABLE
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
        """Assign a rescue mission and begin travelling to its target."""
        if (
            self.state is not RobotState.AVAILABLE
            or not isinstance(mission_id, str)
            or not mission_id
            or not self._is_coordinate(target_latitude, -90.0, 90.0)
            or not self._is_coordinate(target_longitude, -180.0, 180.0)
        ):
            return False
        self._transition(RobotState.DISPATCHED)
        self.mission_id = mission_id
        self.target_latitude = target_latitude
        self.target_longitude = target_longitude
        self._emit(
            SimulationEvent.ROBOT_DISPATCHED,
            {
                "target_latitude": target_latitude,
                "target_longitude": target_longitude,
            },
        )
        self._transition(RobotState.EN_ROUTE)
        return True

    def dispatch_to_person(self, mission_id: str, person) -> bool:
        """Dispatch to a demo Person or a camera detection dictionary."""
        if hasattr(person, "latitude") and hasattr(person, "longitude"):
            latitude = person.latitude
            longitude = person.longitude
        elif isinstance(person, dict):
            latitude = person.get("latitude")
            longitude = person.get("longitude")
        else:
            return False
        if latitude is None or longitude is None:
            return False
        return self.dispatch(mission_id, latitude, longitude)

    def move(self, fraction: float = 0.5) -> bool:
        """Move one deterministic interpolation step toward the target."""
        if self.state is not RobotState.EN_ROUTE:
            return False
        if self.target_latitude is None or self.target_longitude is None:
            return False
        if (
            not isinstance(fraction, (int, float))
            or isinstance(fraction, bool)
            or fraction <= 0.0
            or fraction > 1.0
        ):
            return False

        self.latitude += (self.target_latitude - self.latitude) * fraction
        self.longitude += (self.target_longitude - self.longitude) * fraction
        if abs(self.target_latitude - self.latitude) <= 1e-6:
            self.latitude = self.target_latitude
        if abs(self.target_longitude - self.longitude) <= 1e-6:
            self.longitude = self.target_longitude
        self._consume_battery(1.0)
        if (self.latitude, self.longitude) == (
            self.target_latitude,
            self.target_longitude,
        ):
            self._transition(RobotState.ARRIVED)
            self._emit(
                SimulationEvent.ROBOT_ARRIVED,
                {"latitude": self.latitude, "longitude": self.longitude},
            )
        return True

    def move_to_target(self, fraction: float = 0.5) -> bool:
        """Alias for one deterministic movement step."""
        return self.move(fraction)

    def start_rescue(self) -> bool:
        """Begin the deterministic rescue operation after arrival."""
        if self.state is not RobotState.ARRIVED:
            return False
        self._transition(RobotState.ASSISTING)
        self._consume_battery(1.0)
        self._emit(
            SimulationEvent.RESCUE_STARTED,
            {"latitude": self.latitude, "longitude": self.longitude},
        )
        return True

    def start_assistance(self) -> bool:
        """Alias for beginning the rescue assistance state."""
        return self.start_rescue()

    def complete_rescue(self) -> bool:
        """Mark the deterministic rescue operation complete."""
        if self.state is not RobotState.ASSISTING:
            return False
        self._transition(RobotState.RESCUE_COMPLETE)
        self._consume_battery(1.0)
        self._emit(
            SimulationEvent.RESCUE_COMPLETED,
            {"latitude": self.latitude, "longitude": self.longitude},
        )
        return True

    def return_to_available(self) -> bool:
        """Release the robot for another mission at the rescue location."""
        if self.state is not RobotState.RESCUE_COMPLETE:
            return False
        self._transition(RobotState.AVAILABLE)
        self.mission_id = None
        return True

    def to_dict(self) -> dict:
        """Return the current robot state as JSON-friendly primitives."""
        return {
            "robot_id": self.robot_id,
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

    def _transition(self, requested: RobotState) -> None:
        require_valid_transition(self.state, requested)
        self.state = requested

    def _emit(self, event_type: SimulationEvent, data: dict) -> None:
        self._event_number += 1
        self.events.append(
            SimulationEventRecord(
                event_type=event_type,
                timestamp=self._event_number,
                asset_id=self.robot_id,
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