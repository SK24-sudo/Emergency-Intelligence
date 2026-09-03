"""Tests for the deterministic drone simulator."""

import json
import unittest

from simulation.contract import DroneState, SimulationEvent
from simulation.drone import DroneSimulator


class TestDroneSimulator(unittest.TestCase):
    def make_drone(self, battery=100.0):
        return DroneSimulator(
            "DRONE-01",
            latitude=18.5204,
            longitude=73.8567,
            battery=battery,
            base_latitude=18.5204,
            base_longitude=73.8567,
        )

    def test_initial_state(self):
        drone = self.make_drone()
        self.assertEqual(drone.state, DroneState.AVAILABLE)
        self.assertEqual((drone.latitude, drone.longitude), (18.5204, 73.8567))
        self.assertEqual(drone.battery, 100.0)
        self.assertIsNone(drone.mission_id)

    def test_dispatch_stores_mission_and_target(self):
        drone = self.make_drone()
        self.assertTrue(drone.dispatch("mission-1", 18.5211, 73.8572))
        self.assertEqual(drone.state, DroneState.EN_ROUTE)
        self.assertEqual(drone.mission_id, "mission-1")
        self.assertEqual((drone.target_latitude, drone.target_longitude), (18.5211, 73.8572))
        self.assertEqual(
            [event.event_type for event in drone.events],
            [SimulationEvent.DRONE_DISPATCHED, SimulationEvent.DRONE_EN_ROUTE],
        )

    def test_busy_drone_rejects_second_dispatch(self):
        drone = self.make_drone()
        drone.dispatch("mission-1", 18.5211, 73.8572)
        self.assertFalse(drone.dispatch("mission-2", 18.0, 73.0))
        self.assertEqual(drone.mission_id, "mission-1")

    def test_movement_is_deterministic_and_reaches_target(self):
        first = self.make_drone()
        second = self.make_drone()
        for drone in (first, second):
            drone.dispatch("mission-1", 18.5211, 73.8572)
            for _ in range(40):
                if drone.state is not DroneState.EN_ROUTE:
                    break
                drone.move()
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.state, DroneState.SEARCHING)
        self.assertEqual((first.latitude, first.longitude), (18.5211, 73.8572))
        self.assertIn(SimulationEvent.DRONE_SEARCH_STARTED, [event.event_type for event in first.events])

    def test_detection_and_return_lifecycle(self):
        drone = self.make_drone()
        drone.dispatch("mission-1", 18.5211, 73.8572)
        for _ in range(40):
            if drone.state is not DroneState.EN_ROUTE:
                break
            drone.move()
        self.assertTrue(drone.detect_person())
        self.assertEqual(drone.state, DroneState.PERSON_FOUND)
        self.assertTrue(drone.return_to_base())
        self.assertEqual(drone.state, DroneState.RETURNING)
        for _ in range(40):
            if drone.state is DroneState.AVAILABLE:
                break
            drone.move()
        self.assertEqual(drone.state, DroneState.AVAILABLE)
        self.assertEqual((drone.latitude, drone.longitude), (18.5204, 73.8567))
        self.assertIsNone(drone.mission_id)
        event_types = [event.event_type for event in drone.events]
        self.assertIn(SimulationEvent.PERSON_DETECTED, event_types)
        self.assertIn(SimulationEvent.PERSON_LOCATION_IDENTIFIED, event_types)
        detected = next(
            event for event in drone.events
            if event.event_type is SimulationEvent.PERSON_DETECTED
        )
        self.assertEqual(detected.data["person_id"], "PERSON-001")

    def test_battery_is_deterministic_and_never_negative(self):
        drone = self.make_drone(battery=0.1)
        drone.dispatch("mission-1", 18.5211, 73.8572)
        for _ in range(50):
            if drone.state is DroneState.EN_ROUTE:
                drone.move()
            elif drone.state is DroneState.SEARCHING:
                drone.detect_person()
                drone.return_to_base()
            elif drone.state is DroneState.RETURNING:
                drone.move()
            else:
                break
        self.assertGreaterEqual(drone.battery, 0.0)

    def test_invalid_operations_are_safe(self):
        drone = self.make_drone()
        self.assertFalse(drone.start_search())
        self.assertFalse(drone.detect_person())
        self.assertFalse(drone.return_to_base())
        self.assertFalse(drone.move())
        self.assertFalse(drone.dispatch("", 18.0, 73.0))
        self.assertFalse(drone.dispatch("mission-1", 91.0, 73.0))
        self.assertFalse(drone.dispatch("mission-1", 18.0, 181.0))
        self.assertEqual(drone.state, DroneState.AVAILABLE)

    def test_unknown_person_id_is_rejected(self):
        drone = self.make_drone()
        drone.dispatch("mission-1", 18.5211, 73.8572)
        for _ in range(40):
            if drone.state is not DroneState.EN_ROUTE:
                break
            drone.move()
        self.assertFalse(drone.detect_person("PERSON-UNKNOWN"))
        self.assertEqual(drone.state, DroneState.SEARCHING)
        self.assertEqual(len(drone.events), 3)

    def test_to_dict_is_json_serializable(self):
        payload = self.make_drone().to_dict()
        self.assertEqual(json.loads(json.dumps(payload)), payload)


if __name__ == "__main__":
    unittest.main()