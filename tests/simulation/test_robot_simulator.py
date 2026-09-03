"""Tests for the deterministic robot simulator."""

import json
import unittest

from simulation.contract import RobotState, SimulationEvent
from simulation.data.people import DEMO_PEOPLE
from simulation.robot import RobotSimulator


class TestRobotSimulator(unittest.TestCase):
    def make_robot(self, battery=100.0):
        return RobotSimulator(
            "ROBOT-01",
            latitude=18.5204,
            longitude=73.8567,
            battery=battery,
            base_latitude=18.5204,
            base_longitude=73.8567,
        )

    def reach_target(self, robot):
        for _ in range(40):
            if robot.state is not RobotState.EN_ROUTE:
                break
            robot.move()

    def test_initial_state_and_fields(self):
        robot = self.make_robot()
        self.assertEqual(robot.robot_id, "ROBOT-01")
        self.assertEqual(robot.state, RobotState.AVAILABLE)
        self.assertEqual((robot.latitude, robot.longitude), (18.5204, 73.8567))
        self.assertEqual(robot.battery, 100.0)
        self.assertIsNone(robot.mission_id)

    def test_dispatch_stores_target_and_rejects_busy_robot(self):
        robot = self.make_robot()
        self.assertTrue(robot.dispatch("mission-1", 18.5211, 73.8572))
        self.assertEqual(robot.state, RobotState.EN_ROUTE)
        self.assertEqual(robot.mission_id, "mission-1")
        self.assertEqual((robot.target_latitude, robot.target_longitude), (18.5211, 73.8572))
        self.assertFalse(robot.dispatch("mission-2", 19.0, 74.0))

    def test_deterministic_movement_reaches_target_and_emits_arrival(self):
        first = self.make_robot()
        second = self.make_robot()
        for robot in (first, second):
            robot.dispatch("mission-1", 18.5211, 73.8572)
            self.reach_target(robot)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.state, RobotState.ARRIVED)
        self.assertEqual((first.latitude, first.longitude), (18.5211, 73.8572))
        self.assertIn(
            SimulationEvent.ROBOT_ARRIVED,
            [event.event_type for event in first.events],
        )

    def test_rescue_lifecycle_and_mission_clear(self):
        robot = self.make_robot()
        robot.dispatch_to_person("mission-1", DEMO_PEOPLE[0])
        self.reach_target(robot)
        self.assertTrue(robot.start_rescue())
        self.assertEqual(robot.state, RobotState.ASSISTING)
        self.assertTrue(robot.complete_rescue())
        self.assertEqual(robot.state, RobotState.RESCUE_COMPLETE)
        self.assertTrue(robot.return_to_available())
        self.assertEqual(robot.state, RobotState.AVAILABLE)
        self.assertIsNone(robot.mission_id)
        self.assertEqual(
            [event.event_type for event in robot.events],
            [
                SimulationEvent.ROBOT_DISPATCHED,
                SimulationEvent.ROBOT_ARRIVED,
                SimulationEvent.RESCUE_STARTED,
                SimulationEvent.RESCUE_COMPLETED,
            ],
        )

    def test_rescue_events_and_person_dictionary_target(self):
        robot = self.make_robot()
        self.assertTrue(robot.dispatch_to_person("mission-1", DEMO_PEOPLE[0].to_dict()))
        self.assertEqual(
            (robot.target_latitude, robot.target_longitude),
            (DEMO_PEOPLE[0].latitude, DEMO_PEOPLE[0].longitude),
        )
        self.reach_target(robot)
        robot.start_rescue()
        robot.complete_rescue()
        event_types = [event.event_type for event in robot.events]
        self.assertIn(SimulationEvent.RESCUE_STARTED, event_types)
        self.assertIn(SimulationEvent.RESCUE_COMPLETED, event_types)

    def test_battery_is_deterministic_and_never_negative(self):
        first = self.make_robot(battery=0.1)
        second = self.make_robot(battery=0.1)
        for robot in (first, second):
            robot.dispatch("mission-1", 18.5211, 73.8572)
            self.reach_target(robot)
            robot.start_rescue()
            robot.complete_rescue()
        self.assertEqual(first.battery, second.battery)
        self.assertGreaterEqual(first.battery, 0.0)

    def test_invalid_operations_are_safe(self):
        robot = self.make_robot()
        self.assertFalse(robot.move())
        self.assertFalse(robot.start_rescue())
        self.assertFalse(robot.complete_rescue())
        self.assertFalse(robot.return_to_available())
        self.assertFalse(robot.dispatch_to_person("mission-1", object()))
        self.assertFalse(robot.dispatch("", 18.0, 73.0))
        self.assertFalse(robot.dispatch("mission-1", 91.0, 73.0))
        self.assertFalse(robot.dispatch("mission-1", 18.0, 181.0))
        self.assertEqual(robot.state, RobotState.AVAILABLE)

    def test_to_dict_is_json_serializable(self):
        payload = self.make_robot().to_dict()
        self.assertEqual(json.loads(json.dumps(payload)), payload)


if __name__ == "__main__":
    unittest.main()