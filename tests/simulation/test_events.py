"""Tests for the phase 0 simulation event structure (simulation.events)."""

import json
import unittest

from simulation.contract import (
    DroneState,
    SimulationEvent,
)
from simulation.events import SimulationEventRecord


def sample_event(**overrides):
    values = dict(
        event_type=SimulationEvent.DRONE_DISPATCHED,
        timestamp="2026-01-01T00:00:00Z",
        asset_id="drone-001",
        mission_id="mission-001",
        data={"location": [10.0, 20.0]},
    )
    values.update(overrides)
    return SimulationEventRecord(**values)


class TestEventCreation(unittest.TestCase):
    def test_event_can_be_created(self):
        event = sample_event()
        self.assertEqual(event.event_type, SimulationEvent.DRONE_DISPATCHED)
        self.assertEqual(event.timestamp, "2026-01-01T00:00:00Z")
        self.assertEqual(event.asset_id, "drone-001")
        self.assertEqual(event.mission_id, "mission-001")
        self.assertEqual(event.data, {"location": [10.0, 20.0]})

    def test_defaults_for_optional_fields(self):
        event = SimulationEventRecord(
            event_type=SimulationEvent.RESCUE_COMPLETED,
            timestamp="2026-01-01T00:00:00Z",
        )
        self.assertIsNone(event.asset_id)
        self.assertIsNone(event.mission_id)
        self.assertEqual(event.data, {})

    def test_default_data_dict_is_fresh_per_event(self):
        first = SimulationEventRecord(
            event_type=SimulationEvent.PERSON_DETECTED,
            timestamp="t0",
        )
        second = SimulationEventRecord(
            event_type=SimulationEvent.PERSON_DETECTED,
            timestamp="t0",
        )
        first.data["x"] = 1
        self.assertNotIn("x", second.data)


class TestToDict(unittest.TestCase):
    def test_converts_to_dictionary(self):
        event = sample_event()
        result = event.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(
            set(result),
            {"event_type", "timestamp", "asset_id", "mission_id", "data"},
        )

    def test_event_type_is_the_enum_string_value(self):
        event = sample_event(event_type=SimulationEvent.DRONE_SEARCH_STARTED)
        result = event.to_dict()
        self.assertEqual(result["event_type"], "drone_search_started")
        self.assertIsInstance(result["event_type"], str)

    def test_mutating_returned_dict_does_not_mutate_event(self):
        event = sample_event()
        result = event.to_dict()
        result["data"]["mutated"] = True
        result["asset_id"] = "changed"
        self.assertNotIn("mutated", event.data)
        self.assertEqual(event.asset_id, "drone-001")


class TestJsonSerialization(unittest.TestCase):
    def test_dictionary_can_be_json_serialized(self):
        for representative in [
            SimulationEvent.DRONE_DISPATCHED,
            SimulationEvent.PERSON_LOCATION_IDENTIFIED,
            SimulationEvent.RESCUE_COMPLETED,
        ]:
            with self.subTest(event_type=representative):
                event = sample_event(event_type=representative)
                payload = json.dumps(event.to_dict())
                self.assertIsInstance(payload, str)
                restored = json.loads(payload)
                self.assertEqual(
                    restored["event_type"], representative.value
                )
                self.assertEqual(restored["timestamp"], event.timestamp)
                self.assertEqual(restored["asset_id"], event.asset_id)
                self.assertEqual(restored["mission_id"], event.mission_id)
                self.assertEqual(restored["data"], event.data)


class TestEventTypesUseDefinedSimulationEvents(unittest.TestCase):
    def test_all_defined_event_types_can_be_used(self):
        required = [
            "DRONE_DISPATCHED",
            "DRONE_EN_ROUTE",
            "DRONE_SEARCH_STARTED",
            "PERSON_DETECTED",
            "PERSON_LOCATION_IDENTIFIED",
            "ROBOT_DISPATCHED",
            "ROBOT_ARRIVED",
            "RESCUE_STARTED",
            "RESCUE_COMPLETED",
        ]
        for name in required:
            with self.subTest(event_name=name):
                event_type = SimulationEvent[name]
                event = SimulationEventRecord(
                    event_type=event_type,
                    timestamp="t0",
                )
                self.assertEqual(event.to_dict()["event_type"], event_type.value)

    def test_foreign_type_is_rejected(self):
        with self.assertRaises(TypeError):
            SimulationEventRecord(
                event_type=DroneState.DISPATCHED,
                timestamp="t0",
            )

    def test_plain_string_is_rejected(self):
        with self.assertRaises(TypeError):
            SimulationEventRecord(
                event_type="drone_dispatched",
                timestamp="t0",
            )

    def test_foreign_object_is_rejected(self):
        with self.assertRaises(TypeError):
            SimulationEventRecord(event_type=object(), timestamp="t0")


if __name__ == "__main__":
    unittest.main()