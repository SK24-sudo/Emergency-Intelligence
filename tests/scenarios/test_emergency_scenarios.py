"""Deterministic end-to-end emergency response scenarios."""

import json
import unittest

from simulation.camera import CameraSimulator
from simulation.contract import DroneState, RobotState, SimulationEvent
from simulation.data.drones import DEMO_DRONES
from simulation.data.incidents import DEMO_INCIDENTS
from simulation.data.robots import DEMO_ROBOTS
from simulation.drone import DroneSimulator
from simulation.robot import RobotSimulator


def demo_item(items, item_id):
    return next(item for item in items if item.id == item_id)


def advance_drone(drone):
    for _ in range(40):
        if drone.state is not DroneState.EN_ROUTE:
            break
        drone.move()
    return drone


def advance_robot(robot):
    for _ in range(40):
        if robot.state is not RobotState.EN_ROUTE:
            break
        robot.move()
    return robot


def run_workflow(incident_id, mission_id, drone_id="DRONE-01", robot_id="ROBOT-01"):
    incident = demo_item(DEMO_INCIDENTS, incident_id)
    drone_data = demo_item(DEMO_DRONES, drone_id)
    robot_data = demo_item(DEMO_ROBOTS, robot_id)
    drone = DroneSimulator(
        drone_data.id,
        drone_data.latitude,
        drone_data.longitude,
        drone_data.battery,
        drone_data.latitude,
        drone_data.longitude,
    )
    camera = CameraSimulator("CAMERA-01", drone.drone_id)
    robot = RobotSimulator(
        robot_data.id,
        robot_data.latitude,
        robot_data.longitude,
        robot_data.battery,
        robot_data.latitude,
        robot_data.longitude,
    )

    assert drone.dispatch(mission_id, incident.latitude, incident.longitude)
    advance_drone(drone)
    assert drone.state is DroneState.SEARCHING
    assert camera.activate()
    detection = camera.detect_person()
    assert detection is not None
    assert robot.dispatch_to_person(mission_id, detection)
    advance_robot(robot)
    assert robot.state is RobotState.ARRIVED
    assert robot.start_rescue()
    assert robot.complete_rescue()
    assert robot.return_to_available()

    event_records = drone.events + camera.events + robot.events
    return {
        "incident": incident.to_dict(),
        "drone": drone.to_dict(),
        "camera": camera.to_dict(),
        "person": detection,
        "robot": robot.to_dict(),
        "events": [event.to_dict() for event in event_records],
    }


class TestEmergencyScenarios(unittest.TestCase):
    def test_flood_scenario_completes(self):
        result = run_workflow("inc-pune-flood", "mission-flood")
        self.assertEqual(result["incident"]["priority"], "p1")
        self.assertEqual(result["incident"]["severity"], "critical")
        self.assertEqual(result["drone"]["state"], DroneState.SEARCHING.value)
        self.assertEqual(result["robot"]["state"], RobotState.AVAILABLE.value)
        self.assertIsNone(result["robot"]["mission_id"])

    def test_fire_and_accident_scenarios_are_independent(self):
        fire = run_workflow("inc-nashik-fire", "mission-fire")
        accident = run_workflow("inc-nagpur-accident", "mission-accident")
        self.assertEqual(fire["incident"]["priority"], "p2")
        self.assertEqual(fire["incident"]["severity"], "high")
        self.assertEqual(accident["incident"]["priority"], "p3")
        self.assertEqual(accident["incident"]["severity"], "medium")
        self.assertNotEqual(fire["incident"]["id"], accident["incident"]["id"])
        self.assertEqual(fire["person"], accident["person"])

    def test_multiple_missions_keep_resources_and_events_separate(self):
        first_drone = DroneSimulator("DRONE-01", 18.5204, 73.8567)
        second_drone = DroneSimulator("DRONE-02", 19.9975, 73.7898)
        first_robot = RobotSimulator("ROBOT-01", 18.5204, 73.8567)
        second_robot = RobotSimulator("ROBOT-02", 19.9975, 73.7898)
        flood = demo_item(DEMO_INCIDENTS, "inc-pune-flood")
        fire = demo_item(DEMO_INCIDENTS, "inc-nashik-fire")

        self.assertTrue(first_drone.dispatch("mission-flood", flood.latitude, flood.longitude))
        self.assertTrue(second_drone.dispatch("mission-fire", fire.latitude, fire.longitude))
        self.assertFalse(first_drone.dispatch("mission-fire", fire.latitude, fire.longitude))
        advance_drone(first_drone)
        advance_drone(second_drone)
        camera_one = CameraSimulator("CAMERA-01", first_drone.drone_id)
        camera_two = CameraSimulator("CAMERA-02", second_drone.drone_id)
        camera_one.activate()
        camera_two.activate()
        person_one = camera_one.detect_person()
        person_two = camera_two.detect_person()
        self.assertTrue(first_robot.dispatch_to_person("mission-flood", person_one))
        self.assertTrue(second_robot.dispatch_to_person("mission-fire", person_two))
        self.assertFalse(first_robot.dispatch("mission-fire", 18.0, 73.0))
        advance_robot(first_robot)
        self.assertTrue(first_robot.start_rescue())
        self.assertTrue(first_robot.complete_rescue())
        self.assertTrue(first_robot.return_to_available())
        self.assertEqual(second_robot.state, RobotState.EN_ROUTE)
        self.assertEqual(first_robot.events[0].mission_id, "mission-flood")
        self.assertEqual(second_robot.events[0].mission_id, "mission-fire")
        self.assertEqual(camera_one.events[0].asset_id, "DRONE-01")
        self.assertEqual(camera_two.events[0].asset_id, "DRONE-02")

    def test_resource_availability_rejects_duplicate_assignments(self):
        drones = [
            DroneSimulator(item.id, item.latitude, item.longitude)
            for item in DEMO_DRONES
        ]
        robots = [
            RobotSimulator(item.id, item.latitude, item.longitude)
            for item in DEMO_ROBOTS
        ]
        for index, drone in enumerate(drones):
            self.assertTrue(drone.dispatch(f"mission-{index}", 18.52, 73.85))
            self.assertFalse(drone.dispatch("duplicate", 18.52, 73.85))
        for index, robot in enumerate(robots):
            self.assertTrue(robot.dispatch(f"mission-{index}", 18.52, 73.85))
            self.assertFalse(robot.dispatch("duplicate", 18.52, 73.85))
        self.assertEqual(len(drones), len(DEMO_DRONES))
        self.assertEqual(len(robots), len(DEMO_ROBOTS))
        self.assertFalse(drones[0].dispatch("", 18.52, 73.85))
        self.assertFalse(robots[0].dispatch("", 18.52, 73.85))

    def test_completed_resources_can_accept_new_missions(self):
        drone = DroneSimulator("DRONE-01", 18.5204, 73.8567)
        self.assertTrue(drone.dispatch("mission-1", 18.5211, 73.8572))
        advance_drone(drone)
        self.assertTrue(drone.detect_person())
        self.assertTrue(drone.return_to_base())
        advance_drone(drone)
        for _ in range(40):
            if drone.state is DroneState.RETURNING:
                drone.move()
            else:
                break
        self.assertEqual(drone.state, DroneState.AVAILABLE)
        self.assertTrue(drone.dispatch("mission-2", 18.5211, 73.8572))

        robot = RobotSimulator("ROBOT-01", 18.5204, 73.8567)
        self.assertTrue(robot.dispatch("mission-1", 18.5211, 73.8572))
        advance_robot(robot)
        self.assertTrue(robot.start_rescue())
        self.assertTrue(robot.complete_rescue())
        self.assertTrue(robot.return_to_available())
        self.assertTrue(robot.dispatch("mission-2", 18.5198, 73.8559))

    def test_complete_event_flow_has_expected_order_and_ids(self):
        result = run_workflow("inc-pune-flood", "mission-flow")
        event_types = [event["event_type"] for event in result["events"]]
        expected = [
            SimulationEvent.DRONE_DISPATCHED.value,
            SimulationEvent.DRONE_EN_ROUTE.value,
            SimulationEvent.DRONE_SEARCH_STARTED.value,
            SimulationEvent.PERSON_DETECTED.value,
            SimulationEvent.PERSON_LOCATION_IDENTIFIED.value,
            SimulationEvent.ROBOT_DISPATCHED.value,
            SimulationEvent.ROBOT_ARRIVED.value,
            SimulationEvent.RESCUE_STARTED.value,
            SimulationEvent.RESCUE_COMPLETED.value,
        ]
        self.assertEqual(event_types, expected)
        self.assertEqual(result["person"]["person_id"], "PERSON-001")
        self.assertEqual(result["events"][0]["mission_id"], "mission-flow")
        self.assertEqual(result["events"][5]["mission_id"], "mission-flow")
        self.assertEqual(result["events"][3]["asset_id"], "DRONE-01")
        self.assertEqual(result["events"][5]["asset_id"], "ROBOT-01")
        self.assertEqual(result["events"][3]["data"]["person_id"], "PERSON-001")
        self.assertEqual(result["events"][4]["data"]["person_id"], "PERSON-001")

    def test_results_are_json_friendly(self):
        result = run_workflow("inc-pune-flood", "mission-json")
        self.assertEqual(json.loads(json.dumps(result)), result)

    def test_invalid_actions_are_safe(self):
        drone = DroneSimulator("DRONE-01", 18.5204, 73.8567)
        robot = RobotSimulator("ROBOT-01", 18.5204, 73.8567)
        camera = CameraSimulator("CAMERA-01", "DRONE-01")
        self.assertFalse(drone.move())
        self.assertFalse(drone.start_search())
        self.assertIsNone(camera.detect_person())
        self.assertFalse(robot.start_rescue())
        self.assertFalse(robot.complete_rescue())
        self.assertFalse(robot.return_to_available())

    def test_workflow_is_repeatable(self):
        first = run_workflow("inc-nagpur-accident", "mission-repeat")
        second = run_workflow("inc-nagpur-accident", "mission-repeat")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()