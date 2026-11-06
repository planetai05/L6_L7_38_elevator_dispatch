import os
import sys
import pytest

# Ensure lab6 directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lab6")))

from elevator_dispatch import next_direction, door_action, pick_elevator


# =====================================================================
# Tests for next_direction
# =====================================================================

def test_next_direction_up_with_above_requests():
    """Moving up with requests above current floor continues up."""
    assert next_direction(3, "up", [5, 7]) == "up"


def test_next_direction_up_with_below_requests_only():
    """Moving up with only below requests changes direction to down."""
    assert next_direction(5, "up", [2, 1]) == "down"


def test_next_direction_up_with_no_remaining_requests():
    """Moving up with no above or below requests returns idle."""
    assert next_direction(4, "up", []) == "idle"
    assert next_direction(4, "up", [4]) == "idle"


def test_next_direction_down_with_below_requests():
    """Moving down with requests below current floor continues down."""
    assert next_direction(6, "down", [2, 4]) == "down"


def test_next_direction_down_with_above_requests_only():
    """Moving down with only above requests changes direction to up."""
    assert next_direction(2, "down", [5, 8]) == "up"


def test_next_direction_down_with_no_remaining_requests():
    """Moving down with no above or below requests returns idle."""
    assert next_direction(2, "down", []) == "idle"
    assert next_direction(2, "down", [2]) == "idle"


def test_next_direction_idle_with_above_requests():
    """Idle elevator with requests above chooses up."""
    assert next_direction(1, "idle", [3, 7]) == "up"


def test_next_direction_idle_with_below_requests_only():
    """Idle elevator with only requests below chooses down."""
    assert next_direction(8, "idle", [3, 5]) == "down"


def test_next_direction_idle_with_no_requests():
    """Idle elevator with no requests remains idle."""
    assert next_direction(5, "idle", []) == "idle"
    assert next_direction(5, "idle", [5]) == "idle"


def test_next_direction_unknown_direction_with_requests():
    """Unknown direction falls through to idle-like logic."""
    assert next_direction(2, "stopped", [5]) == "up"
    assert next_direction(7, "stopped", [3]) == "down"
    assert next_direction(4, "stopped", [4]) == "idle"


# =====================================================================
# Tests for door_action
# =====================================================================

def test_door_action_emergency_overrides_everything():
    """Emergency condition must always return hold_open."""
    assert door_action(load_kg=800, blocked=True, emergency=True) == "hold_open"
    assert door_action(load_kg=200, blocked=False, emergency=True) == "hold_open"


def test_door_action_overload_normal():
    """Over capacity without emergency triggers overload."""
    assert door_action(load_kg=650, blocked=False, emergency=False) == "overload"
    assert door_action(load_kg=900, blocked=True, emergency=False) == "overload"


def test_door_action_blocked_normal():
    """Door blocked without overload or emergency triggers reopen."""
    assert door_action(load_kg=400, blocked=True, emergency=False) == "reopen"


def test_door_action_normal_close():
    """Safe conditions with no obstruction closes doors."""
    assert door_action(load_kg=500, blocked=False, emergency=False) == "close"


def test_door_action_boundary_weight_630():
    """Weight exactly at limit (630 kg) should not trigger overload."""
    assert door_action(load_kg=630, blocked=False, emergency=False) == "close"
    assert door_action(load_kg=631, blocked=False, emergency=False) == "overload"


# =====================================================================
# Tests for pick_elevator
# =====================================================================

def test_pick_elevator_empty_fleet():
    """Empty list of elevator cars returns None."""
    assert pick_elevator([], 5) is None


def test_pick_elevator_single_idle_car():
    """Single idle car is selected directly."""
    cars = [("CarA", 3, True)]
    assert pick_elevator(cars, 3) == "CarA"


def test_pick_elevator_single_busy_car():
    """Single busy car is selected with penalty applied."""
    cars = [("CarB", 5, False)]
    assert pick_elevator(cars, 10) == "CarB"


def test_pick_elevator_multiple_cars_idle_closer():
    """Closer idle elevator is preferred over farther elevator."""
    cars = [("CarA", 1, True), ("CarB", 4, True), ("CarC", 9, True)]
    assert pick_elevator(cars, 5) == "CarB"


def test_pick_elevator_penalty_causes_farther_idle_to_win():
    """Busy closer elevator penalized by 5 floors, allowing idle farther car to win."""
    # CarA at floor 5, busy -> gap = |5-6| + 5 = 6
    # CarB at floor 3, idle -> gap = |3-6| = 3
    cars = [("CarA", 5, False), ("CarB", 3, True)]
    assert pick_elevator(cars, 6) == "CarB"


def test_pick_elevator_tie_preserves_first():
    """In case of tie in adjusted gap, the earlier car is retained."""
    cars = [("CarA", 2, True), ("CarB", 6, True)]
    # Target floor 4: CarA gap = 2, CarB gap = 2 -> CarA should win
    assert pick_elevator(cars, 4) == "CarA"
