"""Tests for the shared simulated person model."""

import json
import unittest

from simulation.contract import SimulationEvent
from simulation.data.people import DEMO_PEOPLE
from simulation.events import SimulationEventRecord
from simulation.person import Person


class TestPerson(unittest.TestCase):
    def make_person(self, **overrides):
        values = {
            "person_id": "PERSON-TEST",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "confidence": 0.95,
            "distress": "high",
        }
        values.update(overrides)
        return Person(**values)

    def test_person_fields_and_validation(self):
        person = self.make_person()
        self.assertEqual(person.person_id, "PERSON-TEST")
        self.assertEqual(person.id, "PERSON-TEST")
        self.assertEqual(person.latitude, 18.5204)
        self.assertEqual(person.longitude, 73.8567)
        self.assertEqual(person.confidence, 0.95)
        self.assertEqual(person.distress.value, "high")

    def test_invalid_person_data_is_rejected(self):
        invalid_values = [
            {"person_id": ""},
            {"latitude": 91.0},
            {"longitude": 181.0},
            {"confidence": 1.1},
        ]
        for invalid in invalid_values:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.make_person(**invalid)
        with self.assertRaises(ValueError):
            self.make_person(distress="unknown")

    def test_to_dict_is_json_serializable(self):
        person = self.make_person()
        payload = person.to_dict()
        self.assertEqual(json.loads(json.dumps(payload)), payload)

    def test_events_use_existing_event_system(self):
        person = self.make_person()
        for event_type in (
            SimulationEvent.PERSON_DETECTED,
            SimulationEvent.PERSON_LOCATION_IDENTIFIED,
        ):
            event = SimulationEventRecord(
                event_type=event_type,
                timestamp=1,
                asset_id="DRONE-01",
                data=person.to_dict(),
            )
            self.assertEqual(event.to_dict()["event_type"], event_type.value)

    def test_demo_person_data_is_reused(self):
        demo_person = DEMO_PEOPLE[0]
        person = Person(
            person_id=demo_person.person_id,
            latitude=demo_person.latitude,
            longitude=demo_person.longitude,
            confidence=demo_person.confidence,
            distress=demo_person.distress,
            description=demo_person.description,
        )
        self.assertEqual(person.to_dict(), demo_person.to_dict())

    def test_creation_is_deterministic(self):
        self.assertEqual(self.make_person().to_dict(), self.make_person().to_dict())


if __name__ == "__main__":
    unittest.main()