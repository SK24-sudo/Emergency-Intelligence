"""Tests for the phase 0 state transition rules (simulation.state_machine)."""

import ast
import inspect
import unittest
from pathlib import Path

import simulation.state_machine as state_machine
from simulation.contract import DroneState, MissionState, RobotState
from simulation.state_machine import (
    InvalidTransitionError,
    is_valid_transition,
    require_valid_transition,
)

DRONE_VALID = [
    (DroneState.AVAILABLE, DroneState.DISPATCHED),
    (DroneState.DISPATCHED, DroneState.EN_ROUTE),
    (DroneState.EN_ROUTE, DroneState.SEARCHING),
    (DroneState.SEARCHING, DroneState.PERSON_FOUND),
    (DroneState.PERSON_FOUND, DroneState.RETURNING),
    (DroneState.RETURNING, DroneState.AVAILABLE),
]

ROBOT_VALID = [
    (RobotState.AVAILABLE, RobotState.DISPATCHED),
    (RobotState.DISPATCHED, RobotState.EN_ROUTE),
    (RobotState.EN_ROUTE, RobotState.ARRIVED),
    (RobotState.ARRIVED, RobotState.ASSISTING),
    (RobotState.ASSISTING, RobotState.RESCUE_COMPLETE),
    (RobotState.RESCUE_COMPLETE, RobotState.AVAILABLE),
]

MISSION_VALID = [
    (MissionState.CREATED, MissionState.DISPATCHED),
    (MissionState.DISPATCHED, MissionState.ACTIVE),
    (MissionState.ACTIVE, MissionState.COMPLETED),
]


class TestValidTransitions(unittest.TestCase):
    def test_each_drone_transition_is_valid(self):
        for current, requested in DRONE_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertTrue(is_valid_transition(current, requested))
                # The strict entry point must also accept every valid move.
                require_valid_transition(current, requested)

    def test_each_robot_transition_is_valid(self):
        for current, requested in ROBOT_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertTrue(is_valid_transition(current, requested))
                require_valid_transition(current, requested)

    def test_each_mission_transition_is_valid(self):
        for current, requested in MISSION_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertTrue(is_valid_transition(current, requested))
                require_valid_transition(current, requested)


class TestInvalidTransitions(unittest.TestCase):
    def test_reversed_drone_transitions_are_rejected(self):
        for current, requested in DRONE_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertFalse(is_valid_transition(requested, current))

    def test_reversed_robot_transitions_are_rejected(self):
        for current, requested in ROBOT_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertFalse(is_valid_transition(requested, current))

    def test_reversed_mission_transitions_are_rejected(self):
        for current, requested in MISSION_VALID:
            with self.subTest(current=current, requested=requested):
                self.assertFalse(is_valid_transition(requested, current))

    def test_skipped_states_are_rejected(self):
        skipped = [
            (DroneState.AVAILABLE, DroneState.EN_ROUTE),
            (DroneState.DISPATCHED, DroneState.SEARCHING),
            (DroneState.EN_ROUTE, DroneState.PERSON_FOUND),
            (DroneState.SEARCHING, DroneState.RETURNING),
            (DroneState.PERSON_FOUND, DroneState.AVAILABLE),
            (RobotState.AVAILABLE, RobotState.EN_ROUTE),
            (RobotState.EN_ROUTE, RobotState.ASSISTING),
            (RobotState.ARRIVED, RobotState.RESCUE_COMPLETE),
            (MissionState.CREATED, MissionState.ACTIVE),
            (MissionState.DISPATCHED, MissionState.COMPLETED),
        ]
        for current, requested in skipped:
            with self.subTest(current=current, requested=requested):
                self.assertFalse(is_valid_transition(current, requested))

    def test_same_state_is_rejected(self):
        for state in list(DroneState) + list(RobotState) + list(MissionState):
            with self.subTest(state=state):
                self.assertFalse(is_valid_transition(state, state))

    def test_terminal_mission_state_has_no_next(self):
        self.assertFalse(
            is_valid_transition(MissionState.COMPLETED, MissionState.CREATED)
        )
    def test_cross_machine_transitions_are_rejected(self):
        cross = [
            (DroneState.AVAILABLE, RobotState.DISPATCHED),
            (RobotState.ARRIVED, DroneState.SEARCHING),
            (MissionState.ACTIVE, RobotState.ASSISTING),
        ]
        for current, requested in cross:
            with self.subTest(current=current, requested=requested):
                self.assertFalse(is_valid_transition(current, requested))

    def test_unknown_states_are_rejected(self):
        self.assertFalse(is_valid_transition(object(), DroneState.DISPATCHED))
        self.assertFalse(is_valid_transition("available", DroneState.DISPATCHED))

    def test_require_valid_transition_raises(self):
        with self.assertRaises(InvalidTransitionError):
            require_valid_transition(
                DroneState.AVAILABLE, DroneState.SEARCHING
            )
        with self.assertRaises(InvalidTransitionError):
            require_valid_transition(MissionState.ACTIVE, MissionState.CREATED)

    def test_error_message_names_both_states(self):
        with self.assertRaises(InvalidTransitionError) as caught:
            require_valid_transition(DroneState.AVAILABLE, DroneState.SEARCHING)
        message = str(caught.exception)
        self.assertIn("available", message)
        self.assertIn("searching", message)
        self.assertIn("->", message)


class TestNoExternalDependencies(unittest.TestCase):
    def test_state_machine_imports_only_stdlib_and_simulation(self):
        module_path = Path(inspect.getsourcefile(state_machine))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and node.level == 0:
                    top_level_imports.add(node.module.split(".")[0])

        allowed = {"enum", "simulation", "typing"}
        self.assertIn("simulation", top_level_imports)
        self.assertLessEqual(top_level_imports, allowed)

    def test_suite_runs_under_stdlib_unittest(self):
        # The test class itself is a unittest.TestCase; discovery must work
        # without any third-party test framework (e.g. pytest) installed.
        loader = unittest.defaultTestLoader
        suite = loader.discover("tests/simulation", pattern="test_*.py")
        tests = sum(1 for _ in suite) if hasattr(suite, "__iter__") else 0
        self.assertGreater(tests, 0)


if __name__ == "__main__":
    unittest.main()