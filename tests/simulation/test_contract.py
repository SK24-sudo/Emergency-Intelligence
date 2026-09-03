"""Tests for the phase 0 simulation contract (simulation.contract)."""

import unittest

from simulation.contract import (
    DroneState,
    MissionState,
    RobotState,
    SimulationEvent,
)


class TestDroneState(unittest.TestCase):
    def test_has_exactly_required_members(self):
        expected = {
            "AVAILABLE",
            "DISPATCHED",
            "EN_ROUTE",
            "SEARCHING",
            "PERSON_FOUND",
            "RETURNING",
        }
        self.assertEqual(set(DroneState.__members__), expected)

    def test_values_are_strings(self):
        for state in DroneState:
            self.assertIsInstance(state.value, str)


class TestRobotState(unittest.TestCase):
    def test_has_exactly_required_members(self):
        expected = {
            "AVAILABLE",
            "DISPATCHED",
            "EN_ROUTE",
            "ARRIVED",
            "ASSISTING",
            "RESCUE_COMPLETE",
        }
        self.assertEqual(set(RobotState.__members__), expected)

    def test_values_are_strings(self):
        for state in RobotState:
            self.assertIsInstance(state.value, str)


class TestMissionState(unittest.TestCase):
    def test_has_exactly_required_members(self):
        expected = {"CREATED", "DISPATCHED", "ACTIVE", "COMPLETED"}
        self.assertEqual(set(MissionState.__members__), expected)

    def test_values_are_strings(self):
        for state in MissionState:
            self.assertIsInstance(state.value, str)


class TestSimulationEvent(unittest.TestCase):
    def test_has_exactly_required_members(self):
        expected = {
            "DRONE_DISPATCHED",
            "DRONE_EN_ROUTE",
            "DRONE_SEARCH_STARTED",
            "PERSON_DETECTED",
            "PERSON_LOCATION_IDENTIFIED",
            "ROBOT_DISPATCHED",
            "ROBOT_ARRIVED",
            "RESCUE_STARTED",
            "RESCUE_COMPLETED",
        }
        self.assertEqual(set(SimulationEvent.__members__), expected)

    def test_values_are_strings(self):
        for event in SimulationEvent:
            self.assertIsInstance(event.value, str)


if __name__ == "__main__":
    unittest.main()