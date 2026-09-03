"""Phase 0 state transition rules.

Defines the explicit, valid state transitions for drones, robots, and
missions from the phase 0 contract, plus helpers to query whether a
requested transition is allowed.

Only the transition vocabulary lives here. No drone or robot movement
behavior is implemented.
"""

from simulation.contract import DroneState, MissionState, RobotState

# Explicit valid drone transitions.
DRONE_TRANSITIONS = {
    DroneState.AVAILABLE: {DroneState.DISPATCHED},
    DroneState.DISPATCHED: {DroneState.EN_ROUTE},
    DroneState.EN_ROUTE: {DroneState.SEARCHING},
    DroneState.SEARCHING: {DroneState.PERSON_FOUND},
    DroneState.PERSON_FOUND: {DroneState.RETURNING},
    DroneState.RETURNING: {DroneState.AVAILABLE},
}

# Explicit valid robot transitions.
ROBOT_TRANSITIONS = {
    RobotState.AVAILABLE: {RobotState.DISPATCHED},
    RobotState.DISPATCHED: {RobotState.EN_ROUTE},
    RobotState.EN_ROUTE: {RobotState.ARRIVED},
    RobotState.ARRIVED: {RobotState.ASSISTING},
    RobotState.ASSISTING: {RobotState.RESCUE_COMPLETE},
    RobotState.RESCUE_COMPLETE: {RobotState.AVAILABLE},
}

# Explicit valid mission transitions.
MISSION_TRANSITIONS = {
    MissionState.CREATED: {MissionState.DISPATCHED},
    MissionState.DISPATCHED: {MissionState.ACTIVE},
    MissionState.ACTIVE: {MissionState.COMPLETED},
}


class InvalidTransitionError(ValueError):
    """Raised when a requested state transition is not allowed."""


def _transitions_for(state):
    """Return the allowed next states for a contract state.

    Terminal states (such as ``MissionState.COMPLETED``) have no outgoing
    transitions and map to an empty set.
    """
    if isinstance(state, DroneState):
        return DRONE_TRANSITIONS.get(state, set())
    if isinstance(state, RobotState):
        return ROBOT_TRANSITIONS.get(state, set())
    if isinstance(state, MissionState):
        return MISSION_TRANSITIONS.get(state, set())
    raise InvalidTransitionError(f"Unknown state: {state!r}")


def is_valid_transition(current, requested):
    """Return whether ``requested`` is a valid next state for ``current``.

    Accepts any two states and returns ``False`` when the transition is not
    one of the explicitly allowed transitions (including skipped states,
    reversed transitions, self-transitions, and mismatched state types).
    ``current`` and ``requested`` must belong to the same state machine.
    """
    if type(current) is not type(requested):
        return False
    try:
        transitions = _transitions_for(current)
    except InvalidTransitionError:
        return False
    return requested in transitions


def require_valid_transition(current, requested):
    """Reject an invalid transition with a descriptive error.

    Returns ``None`` when ``current -> requested`` is an explicitly allowed
    transition; raises ``InvalidTransitionError`` otherwise, including when
    the two states belong to different state machines.
    """
    if type(current) is not type(requested):
        raise InvalidTransitionError(
            f"Invalid transition: {current} -> {requested}"
        )
    transitions = _transitions_for(current)
    if requested not in transitions:
        raise InvalidTransitionError(
            f"Invalid transition: {current} -> {requested}"
        )