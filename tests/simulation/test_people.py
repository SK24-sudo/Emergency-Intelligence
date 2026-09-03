"""Tests for the phase 1 person demo data (simulation.data.people)."""

import ast
import inspect
import json
import unittest
from pathlib import Path

import simulation.data.people as people
from simulation.data.people import DEMO_PEOPLE, Distress, Person


class TestDemoPeople(unittest.TestCase):
    def test_contains_person_001_and_more(self):
        ids = [person.id for person in DEMO_PEOPLE]
        self.assertIn("PERSON-001", ids)
        self.assertGreaterEqual(len(ids), 1)

    def test_person_ids_are_unique(self):
        ids = [person.id for person in DEMO_PEOPLE]
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_person_has_all_required_fields(self):
        field_names = {
            "id",
            "latitude",
            "longitude",
            "confidence",
            "distress",
            "description",
        }
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                self.assertEqual(set(vars(person)), field_names)

    def test_confidence_is_between_0_and_1(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                self.assertIsInstance(person.confidence, float)
                self.assertGreaterEqual(person.confidence, 0.0)
                self.assertLessEqual(person.confidence, 1.0)

    def test_person_001_distress_is_high(self):
        person_001 = next(p for p in DEMO_PEOPLE if p.id == "PERSON-001")
        self.assertEqual(person_001.distress, Distress.HIGH)

    def test_all_distress_is_high(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                self.assertEqual(person.distress, Distress.HIGH)

    def test_values_are_for_pune_flood_scenario(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                self.assertAlmostEqual(person.latitude, 18.52, places=1)
                self.assertAlmostEqual(person.longitude, 73.85, places=1)

    def test_values_are_deterministic(self):
        first = [json.dumps(p.to_dict(), sort_keys=True) for p in DEMO_PEOPLE]
        second = [json.dumps(p.to_dict(), sort_keys=True) for p in DEMO_PEOPLE]
        self.assertEqual(first, second)


class TestPersonJsonFriendliness(unittest.TestCase):
    def test_to_dict_has_expected_json_friendly_types(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                payload = person.to_dict()
                self.assertIsInstance(payload["id"], str)
                self.assertIsInstance(payload["latitude"], float)
                self.assertIsInstance(payload["longitude"], float)
                self.assertIsInstance(payload["confidence"], float)
                self.assertIsInstance(payload["distress"], str)
                self.assertIsInstance(payload["description"], str)

    def test_distress_is_contract_string_value(self):
        self.assertEqual(DEMO_PEOPLE[0].to_dict()["distress"], "high")

    def test_round_trips_through_json(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                restored = json.loads(json.dumps(person.to_dict()))
                self.assertEqual(restored, person.to_dict())
                self.assertEqual(restored["id"], person.id)


class TestNoMedicalCertainty(unittest.TestCase):
    def test_descriptions_do_not_claim_medical_certainty(self):
        for person in DEMO_PEOPLE:
            with self.subTest(person=person.id):
                lowered = person.description.lower()
                self.assertNotIn("injury", lowered)
                self.assertNotIn("injured", lowered)
                self.assertNotIn("medical", lowered)


class TestNoExternalDependencies(unittest.TestCase):
    def test_people_module_imports_only_stdlib(self):
        module_path = Path(inspect.getsourcefile(people))
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