"""Tests for the deterministic camera simulator."""

import json
import unittest

from simulation.camera import CameraSimulator
from simulation.contract import SimulationEvent
from simulation.data.people import DEMO_PEOPLE


class TestCameraSimulator(unittest.TestCase):
    def make_camera(self):
        return CameraSimulator("CAMERA-01", "DRONE-01")

    def test_creation_and_initial_state(self):
        camera = self.make_camera()
        self.assertEqual(camera.camera_id, "CAMERA-01")
        self.assertEqual(camera.drone_id, "DRONE-01")
        self.assertEqual(camera.status, CameraSimulator.OFF)
        self.assertFalse(camera.is_active())

    def test_activation_and_deactivation(self):
        camera = self.make_camera()
        self.assertTrue(camera.activate())
        self.assertEqual(camera.status, CameraSimulator.ACTIVE)
        self.assertTrue(camera.is_active())
        self.assertFalse(camera.activate())
        self.assertTrue(camera.deactivate())
        self.assertEqual(camera.status, CameraSimulator.OFF)
        self.assertFalse(camera.deactivate())

    def test_active_camera_produces_deterministic_json_frame(self):
        first = self.make_camera()
        second = self.make_camera()
        first.activate()
        second.activate()
        frame_one = first.capture_frame()
        frame_two = second.capture_frame()
        self.assertEqual(frame_one, frame_two)
        self.assertEqual(frame_one["frame_id"], 1)
        self.assertTrue(frame_one["simulated"])
        self.assertEqual(json.loads(json.dumps(frame_one)), frame_one)

    def test_inactive_camera_cannot_capture_or_detect(self):
        camera = self.make_camera()
        self.assertIsNone(camera.capture_frame())
        self.assertIsNone(camera.detect_person())

    def test_person_detection_uses_demo_data_and_events(self):
        camera = self.make_camera()
        camera.activate()
        detection = camera.detect_person()
        expected = DEMO_PEOPLE[0].to_dict()
        self.assertEqual(detection["person_id"], expected["id"])
        self.assertEqual(
            (detection["latitude"], detection["longitude"]),
            (expected["latitude"], expected["longitude"]),
        )
        self.assertEqual(detection["confidence"], expected["confidence"])
        self.assertEqual(detection["distress"], expected["distress"])
        self.assertEqual(
            [event.event_type for event in camera.events],
            [
                SimulationEvent.PERSON_DETECTED,
                SimulationEvent.PERSON_LOCATION_IDENTIFIED,
            ],
        )
        self.assertEqual(json.loads(json.dumps(detection)), detection)

    def test_detection_is_deterministic(self):
        first = self.make_camera()
        second = self.make_camera()
        first.activate()
        second.activate()
        self.assertEqual(first.detect_person(), second.detect_person())

    def test_to_dict_is_json_serializable(self):
        camera = self.make_camera()
        camera.activate()
        camera.capture_frame()
        payload = camera.to_dict()
        self.assertEqual(json.loads(json.dumps(payload)), payload)

    def test_invalid_operations_are_safe(self):
        camera = self.make_camera()
        self.assertFalse(camera.deactivate())
        self.assertIsNone(camera.capture_frame())
        self.assertTrue(camera.activate())
        self.assertFalse(camera.activate())
        self.assertTrue(camera.deactivate())
        self.assertFalse(camera.deactivate())

    def test_unknown_person_id_is_rejected(self):
        camera = self.make_camera()
        camera.activate()
        self.assertIsNone(camera.detect_person("PERSON-UNKNOWN"))
        self.assertEqual(camera.events, [])


if __name__ == "__main__":
    unittest.main()