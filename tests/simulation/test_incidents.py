"""Tests for the phase 1 incident demo data (simulation.data.incidents)."""

import ast
import inspect
import json
import unittest
from pathlib import Path

import simulation.data.incidents as incidents
from simulation.data.incidents import (
    DEMO_INCIDENTS,
    Incident,
    Priority,
    Severity,
)


class TestDemoIncidents(unittest.TestCase):
    def test_contains_the_three_required_incidents(self):
        names = {(i.name, i.severity, i.priority) for i in DEMO_INCIDENTS}
        expected = {
            ("Pune Flood", Severity.CRITICAL, Priority.P1),
            ("Nashik Fire", Severity.HIGH, Priority.P2),
            ("Nagpur Accident", Severity.MEDIUM, Priority.P3),
        }
        self.assertEqual(names, expected)

    def test_pune_flood(self):
        incident = next(i for i in DEMO_INCIDENTS if i.name == "Pune Flood")
        self.assertEqual(incident.severity, Severity.CRITICAL)
        self.assertEqual(incident.priority, Priority.P1)

    def test_nashik_fire(self):
        incident = next(i for i in DEMO_INCIDENTS if i.name == "Nashik Fire")
        self.assertEqual(incident.severity, Severity.HIGH)
        self.assertEqual(incident.priority, Priority.P2)

    def test_nagpur_accident(self):
        incident = next(i for i in DEMO_INCIDENTS if i.name == "Nagpur Accident")
        self.assertEqual(incident.severity, Severity.MEDIUM)
        self.assertEqual(incident.priority, Priority.P3)

    def test_each_incident_has_all_required_fields(self):
        field_names = {
            "id",
            "name",
            "type",
            "severity",
            "priority",
            "latitude",
            "longitude",
            "description",
        }
        for incident in DEMO_INCIDENTS:
            with self.subTest(incident=incident.name):
                self.assertEqual(
                    set(vars(incident)), field_names
                )

    def test_coordinates_are_fixed_floats(self):
        for incident in DEMO_INCIDENTS:
            with self.subTest(incident=incident.name):
                self.assertIsInstance(incident.latitude, float)
                self.assertIsInstance(incident.longitude, float)
                self.assertAlmostEqual(
                    incident.latitude, float(incident.latitude), places=4
                )

    def test_values_are_deterministic(self):
        first = [json.dumps(i.to_dict(), sort_keys=True) for i in DEMO_INCIDENTS]
        second = [
            json.dumps(i.to_dict(), sort_keys=True) for i in DEMO_INCIDENTS
        ]
        self.assertEqual(first, second)


class TestIncidentJsonFriendliness(unittest.TestCase):
    def test_to_dict_has_expected_json_friendly_types(self):
        for incident in DEMO_INCIDENTS:
            with self.subTest(incident=incident.name):
                payload = incident.to_dict()
                for key in ("id", "name", "type", "description"):
                    self.assertIsInstance(payload[key], str)
                self.assertIsInstance(payload["severity"], str)
                self.assertIsInstance(payload["priority"], str)
                self.assertIsInstance(payload["latitude"], float)
                self.assertIsInstance(payload["longitude"], float)

    def test_round_trips_through_json(self):
        for incident in DEMO_INCIDENTS:
            with self.subTest(incident=incident.name):
                restored = json.loads(json.dumps(incident.to_dict()))
                self.assertEqual(restored, incident.to_dict())
                self.assertEqual(restored["name"], incident.name)


class TestNoExternalDependencies(unittest.TestCase):
    def test_incidents_module_imports_only_stdlib(self):
        module_path = Path(inspect.getsourcefile(incidents))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and node.level == 0:
                    top_level_imports.add(node.module.split(".")[0])
        self.assertLessEqual(top_level_imports, {"dataclasses", "enum"})


if __name__ == "__main__":
    unittest.main()