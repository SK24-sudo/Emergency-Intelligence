"""Tests for the phase 1 robot demo data (simulation.data.robots)."""

import ast
import inspect
import json
import unittest
from pathlib import Path

import simulation.data.robots as robots
from simulation.contract import RobotState
from simulation.data.robots import DEMO_ROBOTS, Robot


class TestDemoRobots(unittest.TestCase):
    def test_contains_the_two_required_robots(self):
        self.assertEqual(
            [robot.id for robot in DEMO_ROBOTS],
            ["ROBOT-01", "ROBOT-02"],
        )

    def test_robot_ids_are_unique(self):
        ids = [robot.id for robot in DEMO_ROBOTS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_status_defaults_to_available(self):
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                self.assertEqual(robot.status, RobotState.AVAILABLE)

    def test_status_is_robot_state_member(self):
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                self.assertIsInstance(robot.status, RobotState)

    def test_each_robot_has_all_required_fields(self):
        field_names = {
            "id",
            "name",
            "status",
            "latitude",
            "longitude",
            "battery",
            "current_mission",
        }
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                self.assertEqual(set(vars(robot)), field_names)

    def test_coordinates_and_battery_are_fixed(self):
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                self.assertIsInstance(robot.latitude, float)
                self.assertIsInstance(robot.longitude, float)
                self.assertIsInstance(robot.battery, float)
                self.assertGreaterEqual(robot.battery, 0.0)
                self.assertLessEqual(robot.battery, 100.0)

    def test_values_are_deterministic(self):
        first = [json.dumps(r.to_dict(), sort_keys=True) for r in DEMO_ROBOTS]
        second = [json.dumps(r.to_dict(), sort_keys=True) for r in DEMO_ROBOTS]
        self.assertEqual(first, second)


class TestRobotJsonFriendliness(unittest.TestCase):
    def test_to_dict_has_expected_json_friendly_types(self):
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                payload = robot.to_dict()
                self.assertIsInstance(payload["id"], str)
                self.assertIsInstance(payload["name"], str)
                self.assertIsInstance(payload["status"], str)
                self.assertIsInstance(payload["latitude"], float)
                self.assertIsInstance(payload["longitude"], float)
                self.assertIsInstance(payload["battery"], float)
                self.assertIsNone(payload["current_mission"])

    def test_status_uses_contract_string_value(self):
        self.assertEqual(
            DEMO_ROBOTS[0].to_dict()["status"], RobotState.AVAILABLE.value
        )

    def test_round_trips_through_json(self):
        for robot in DEMO_ROBOTS:
            with self.subTest(robot=robot.id):
                restored = json.loads(json.dumps(robot.to_dict()))
                self.assertEqual(restored, robot.to_dict())
                self.assertEqual(restored["id"], robot.id)


class TestNoExternalDependencies(unittest.TestCase):
    def test_robots_module_imports_only_stdlib_and_simulation(self):
        module_path = Path(inspect.getsourcefile(robots))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and node.level == 0:
                    top_level_imports.add(node.module.split(".")[0])
        self.assertLessEqual(
            top_level_imports, {"dataclasses", "typing", "simulation"}
        )
        self.assertIn("simulation", top_level_imports)


if __name__ == "__main__":
    unittest.main()