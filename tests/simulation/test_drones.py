"""Tests for the phase 1 drone demo data (simulation.data.drones)."""

import ast
import inspect
import json
import unittest
from pathlib import Path

import simulation.data.drones as drones
from simulation.contract import DroneState
from simulation.data.drones import DEMO_DRONES, Drone


class TestDemoDrones(unittest.TestCase):
    def test_contains_the_three_required_drones(self):
        self.assertEqual(
            [drone.id for drone in DEMO_DRONES],
            ["DRONE-01", "DRONE-02", "DRONE-03"],
        )

    def test_drone_ids_are_unique(self):
        ids = [drone.id for drone in DEMO_DRONES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_status_defaults_to_available(self):
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                self.assertEqual(drone.status, DroneState.AVAILABLE)

    def test_status_is_drone_state_member(self):
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                self.assertIsInstance(drone.status, DroneState)

    def test_each_drone_has_all_required_fields(self):
        field_names = {
            "id",
            "name",
            "status",
            "latitude",
            "longitude",
            "battery",
            "current_mission",
        }
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                self.assertEqual(set(vars(drone)), field_names)

    def test_coordinates_and_battery_are_fixed(self):
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                self.assertIsInstance(drone.latitude, float)
                self.assertIsInstance(drone.longitude, float)
                self.assertIsInstance(drone.battery, float)
                self.assertGreaterEqual(drone.battery, 0.0)
                self.assertLessEqual(drone.battery, 100.0)

    def test_values_are_deterministic(self):
        first = [json.dumps(d.to_dict(), sort_keys=True) for d in DEMO_DRONES]
        second = [json.dumps(d.to_dict(), sort_keys=True) for d in DEMO_DRONES]
        self.assertEqual(first, second)


class TestDroneJsonFriendliness(unittest.TestCase):
    def test_to_dict_has_expected_json_friendly_types(self):
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                payload = drone.to_dict()
                self.assertIsInstance(payload["id"], str)
                self.assertIsInstance(payload["name"], str)
                self.assertIsInstance(payload["status"], str)
                self.assertIsInstance(payload["latitude"], float)
                self.assertIsInstance(payload["longitude"], float)
                self.assertIsInstance(payload["battery"], float)
                self.assertIsNone(payload["current_mission"])

    def test_status_uses_contract_string_value(self):
        self.assertEqual(
            DEMO_DRONES[0].to_dict()["status"], DroneState.AVAILABLE.value
        )

    def test_round_trips_through_json(self):
        for drone in DEMO_DRONES:
            with self.subTest(drone=drone.id):
                restored = json.loads(json.dumps(drone.to_dict()))
                self.assertEqual(restored, drone.to_dict())
                self.assertEqual(restored["id"], drone.id)


class TestNoExternalDependencies(unittest.TestCase):
    def test_drones_module_imports_only_stdlib_and_simulation(self):
        module_path = Path(inspect.getsourcefile(drones))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and node.level == 0:
                    top_level_imports.add(node.module.split(".")[0])
        self.assertLessEqual(top_level_imports, {"dataclasses", "typing", "simulation"})
        self.assertIn("simulation", top_level_imports)


if __name__ == "__main__":
    unittest.main()