"""Tests for the phase 1 data access layer (simulation.data)."""

import ast
import inspect
import json
import unittest
from pathlib import Path

import simulation.data as data


class TestDataAccessors(unittest.TestCase):
    def test_get_incidents_returns_list_of_dicts(self):
        incidents = data.get_incidents()
        self.assertIsInstance(incidents, list)
        for incident in incidents:
            with self.subTest(incident=incident.get("name")):
                self.assertIsInstance(incident, dict)
                json.dumps(incident)  # must be JSON-friendly

    def test_get_drones_returns_list_of_dicts(self):
        drones = data.get_drones()
        self.assertIsInstance(drones, list)
        for drone in drones:
            with self.subTest(drone=drone.get("id")):
                self.assertIsInstance(drone, dict)
                json.dumps(drone)

    def test_get_robots_returns_list_of_dicts(self):
        robots = data.get_robots()
        self.assertIsInstance(robots, list)
        for robot in robots:
            with self.subTest(robot=robot.get("id")):
                self.assertIsInstance(robot, dict)
                json.dumps(robot)

    def test_get_people_returns_list_of_dicts(self):
        people = data.get_people()
        self.assertIsInstance(people, list)
        for person in people:
            with self.subTest(person=person.get("id")):
                self.assertIsInstance(person, dict)
                json.dumps(person)

    def test_counts_match_demo_data(self):
        self.assertEqual(len(data.get_incidents()), 3)
        self.assertEqual(len(data.get_drones()), 3)
        self.assertEqual(len(data.get_robots()), 2)
        self.assertGreaterEqual(len(data.get_people()), 1)

    def test_ids_match_demo_data(self):
        self.assertEqual(
            [i["id"] for i in data.get_incidents()],
            ["inc-pune-flood", "inc-nashik-fire", "inc-nagpur-accident"],
        )
        self.assertEqual(
            [d["id"] for d in data.get_drones()],
            ["DRONE-01", "DRONE-02", "DRONE-03"],
        )
        self.assertEqual(
            [r["id"] for r in data.get_robots()],
            ["ROBOT-01", "ROBOT-02"],
        )
        self.assertIn("PERSON-001", [p["id"] for p in data.get_people()])

    def test_json_round_trip(self):
        payloads = []
        payloads.extend(data.get_incidents())
        payloads.extend(data.get_drones())
        payloads.extend(data.get_robots())
        payloads.extend(data.get_people())
        self.assertTrue(payloads)
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(json.loads(json.dumps(payload)), payload)

    def test_returns_fresh_lists(self):
        for func in (data.get_incidents, data.get_drones, data.get_robots, data.get_people):
            with self.subTest(func=func.__name__):
                first = func()
                second = func()
                self.assertEqual(first, second)
                if first:
                    first[0]["mutated"] = True
                    self.assertNotIn("mutated", second[0])
                    self.assertNotIn("mutated", func()[0])

    def test_status_and_enum_values_use_contract_strings(self):
        drone_states = {
            "available", "dispatched", "en_route", "searching", "person_found", "returning",
        }
        robot_states = {
            "available", "dispatched", "en_route", "arrived", "assisting", "rescue_complete",
        }
        for drone in data.get_drones():
            with self.subTest(drone=drone["id"]):
                self.assertIn(drone["status"], drone_states)
 
        for robot in data.get_robots():
            with self.subTest(robot=robot["id"]):
                self.assertIn(robot["status"], robot_states)
 
        for incident in data.get_incidents():
            with self.subTest(incident=incident["id"]):
                self.assertIn(incident["severity"], {"critical", "high", "medium", "low"})
                self.assertIn(incident["priority"], {"p1", "p2", "p3"})
 
        for person in data.get_people():
            with self.subTest(person=person["id"]):
                self.assertIsInstance(person["confidence"], float)
                self.assertGreaterEqual(person["confidence"], 0.0)
                self.assertLessEqual(person["confidence"], 1.0)


class TestNoExternalDependencies(unittest.TestCase):
    def test_data_package_imports_only_local_modules(self):
        module_path = Path(inspect.getsourcefile(data))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        absolute_imports = set()
        relative_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    absolute_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:
                    if node.module is not None:
                        absolute_imports.add(node.module.split(".")[0])
                elif node.module is not None:
                    relative_imports.add(node.module.split(".")[0])
        self.assertLessEqual(absolute_imports, set())
        self.assertLessEqual(relative_imports, {"drones", "incidents", "people", "robots"})
        self.assertTrue(relative_imports)


if __name__ == "__main__":
    unittest.main()