import os
import sys
import pytest

# Ensure lab6 directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lab6")))

from elevator_dispatch import next_direction, door_action, pick_elevator


# =====================================================================
# Branch Coverage Tests for next_direction
# =====================================================================

class TestNextDirectionBranchCoverage:
    """Tests covering all decision branches in next_direction."""

    def test_branch_direction_up_above_true(self):
        # direction == "up" (True) -> above (True) -> returns "up"
        assert next_direction(current=5, direction="up", requests=[7, 10]) == "up"

    def test_branch_direction_up_above_false_below_true(self):
        # direction == "up" (True) -> above (False) -> below (True) -> returns "down"
        assert next_direction(current=5, direction="up", requests=[2, 4]) == "down"

    def test_branch_direction_up_above_false_below_false(self):
        # direction == "up" (True) -> above (False) -> below (False) -> returns "idle"
        # 1) empty requests
        assert next_direction(current=5, direction="up", requests=[]) == "idle"
        # 2) request at the same floor (neither above nor below)
        assert next_direction(current=5, direction="up", requests=[5]) == "idle"

    def test_branch_direction_down_below_true(self):
        # direction == "up" (False) -> direction == "down" (True) -> below (True) -> returns "down"
        assert next_direction(current=6, direction="down", requests=[1, 3]) == "down"

    def test_branch_direction_down_below_false_above_true(self):
        # direction == "up" (False) -> direction == "down" (True) -> below (False) -> above (True) -> returns "up"
        assert next_direction(current=3, direction="down", requests=[8, 9]) == "up"

    def test_branch_direction_down_below_false_above_false(self):
        # direction == "up" (False) -> direction == "down" (True) -> below (False) -> above (False) -> returns "idle"
        # 1) empty requests
        assert next_direction(current=3, direction="down", requests=[]) == "idle"
        # 2) request at same floor
        assert next_direction(current=3, direction="down", requests=[3]) == "idle"

    def test_branch_direction_other_above_true(self):
        # direction == "up" (False) -> direction == "down" (False) -> above (True) -> returns "up"
        assert next_direction(current=2, direction="idle", requests=[4, 6]) == "up"
        assert next_direction(current=2, direction="stopped", requests=[5]) == "up"

    def test_branch_direction_other_above_false_below_true(self):
        # direction == "up" (False) -> direction == "down" (False) -> above (False) -> below (True) -> returns "down"
        assert next_direction(current=8, direction="idle", requests=[2, 4]) == "down"
        assert next_direction(current=8, direction="maintenance", requests=[3]) == "down"

    def test_branch_direction_other_above_false_below_false(self):
        # direction == "up" (False) -> direction == "down" (False) -> above (False) -> below (False) -> returns "idle"
        assert next_direction(current=4, direction="idle", requests=[]) == "idle"
        assert next_direction(current=4, direction="idle", requests=[4]) == "idle"
        assert next_direction(current=4, direction=None, requests=[]) == "idle"


# =====================================================================
# Branch Coverage Tests for door_action
# =====================================================================

class TestDoorActionBranchCoverage:
    """Tests covering all decision branches and truth value combos for door_action."""

    def test_branch_emergency_true(self):
        # emergency (True) -> returns "hold_open" regardless of load or blocked state
        # 1) emergency True, overload True, blocked True
        assert door_action(load_kg=700, blocked=True, emergency=True) == "hold_open"
        # 2) emergency True, overload False, blocked False
        assert door_action(load_kg=400, blocked=False, emergency=True) == "hold_open"
        # 3) emergency True, overload True, blocked False
        assert door_action(load_kg=750, blocked=False, emergency=True) == "hold_open"
        # 4) emergency True, overload False, blocked True
        assert door_action(load_kg=300, blocked=True, emergency=True) == "hold_open"

    def test_branch_emergency_false_load_greater_630_true(self):
        # emergency (False) -> load_kg > 630 (True) -> returns "overload"
        # Boundary: 631 > 630 is True
        assert door_action(load_kg=631, blocked=False, emergency=False) == "overload"
        assert door_action(load_kg=800, blocked=True, emergency=False) == "overload"

    def test_branch_emergency_false_load_greater_630_false_blocked_true(self):
        # emergency (False) -> load_kg > 630 (False) -> blocked (True) -> returns "reopen"
        # Boundary: 630 > 630 is False
        assert door_action(load_kg=630, blocked=True, emergency=False) == "reopen"
        assert door_action(load_kg=450, blocked=True, emergency=False) == "reopen"

    def test_branch_emergency_false_load_greater_630_false_blocked_false(self):
        # emergency (False) -> load_kg > 630 (False) -> blocked (False) -> returns "close"
        # Boundary: 630 > 630 is False
        assert door_action(load_kg=630, blocked=False, emergency=False) == "close"
        # Boundary: 629 > 630 is False
        assert door_action(load_kg=629, blocked=False, emergency=False) == "close"
        assert door_action(load_kg=0, blocked=False, emergency=False) == "close"


# =====================================================================
# Branch Coverage Tests for pick_elevator
# =====================================================================

class TestPickElevatorBranchCoverage:
    """Tests covering all branches in pick_elevator."""

    def test_branch_empty_cars_loop_zero_iterations(self):
        # for car in cars -> 0 iterations -> returns best (None)
        assert pick_elevator([], 5) is None

    def test_branch_single_car_idle_true(self):
        # 1 iteration:
        # not is_idle (False) -> gap not increased
        # best is None (True) -> best becomes car name
        cars = [("Alpha", 4, True)]
        assert pick_elevator(cars, 4) == "Alpha"

    def test_branch_single_car_idle_false(self):
        # 1 iteration:
        # not is_idle (True) -> gap increased by 5
        # best is None (True) -> best becomes car name
        cars = [("Beta", 4, False)]
        assert pick_elevator(cars, 4) == "Beta"

    def test_branch_multiple_cars_best_none_false_gap_less_true(self):
        # Iteration 1: best is None (True) -> best = Car1
        # Iteration 2: best is None (False) -> gap < best_gap (True) -> best = Car2
        cars = [
            ("CarFar", 10, True),    # gap = |10-2| = 8
            ("CarClose", 3, True)    # gap = |3-2| = 1 < 8 -> replaces CarFar
        ]
        assert pick_elevator(cars, 2) == "CarClose"

    def test_branch_multiple_cars_best_none_false_gap_less_false(self):
        # Iteration 1: best is None (True) -> best = CarClose
        # Iteration 2: best is None (False) -> gap < best_gap (False) -> retains CarClose
        cars = [
            ("CarClose", 3, True),   # gap = |3-2| = 1
            ("CarFar", 10, True)     # gap = |10-2| = 8 (not < 1) -> does not replace
        ]
        assert pick_elevator(cars, 2) == "CarClose"

    def test_branch_multiple_cars_gap_tie_retains_earlier_car(self):
        # Iteration 2: gap == best_gap -> gap < best_gap evaluates to False
        cars = [
            ("Car1", 3, True),       # gap = |3-5| = 2
            ("Car2", 7, True)        # gap = |7-5| = 2 (not < 2) -> Car1 retained
        ]
        assert pick_elevator(cars, 5) == "Car1"

    def test_branch_busy_penalty_inversion(self):
        # Busy car closer (gap 1 + 5 = 6) vs idle car further (gap 4)
        # Iteration 1: BusyCar -> best_gap = 6
        # Iteration 2: IdleCar -> gap = 4 < 6 -> IdleCar selected
        cars = [
            ("BusyCar", 6, False),   # floor 5: gap = |6-5| + 5 = 6
            ("IdleCar", 1, True)     # floor 5: gap = |1-5| = 4 < 6
        ]
        assert pick_elevator(cars, 5) == "IdleCar"
