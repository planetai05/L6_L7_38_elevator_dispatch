# Lab 6: Code and Branch Coverage Analysis

## 1. Student Details
- **Student Name:** Anish A Kunder
- **SRN:** PES1UG24AM343
- **Repository:** https://github.com/planetai05/L6_L7_38_elevator_dispatch
- **Branch:** `lab6-lab7-solutions`

---

## 2. Lab Title & Objective
**Title:** Lab 6: Code and Branch Coverage Analysis  
**Objective:**
- Understand the fundamental differences between code (statement/line) coverage and branch (decision) coverage.
- Utilize Python's `coverage` tool to measure, analyze, and systematically improve test coverage.
- Interpret coverage reports and identify untested logical paths and boundary conditions.
- Design targeted pytest test suites to achieve minimum 90% (specifically **100%**) line and branch coverage on the assigned elevator dispatch application.

---

## 3. Application Description
The application under test is `elevator_dispatch.py` (under `lab6/elevator_dispatch.py`). It implements dispatch, door management, and car allocation logic for a multi-car elevator control system through three primary functions:
1. **`next_direction(current, direction, requests)`**:
   - Determines the next direction of elevator movement (`"up"`, `"down"`, or `"idle"`) based on the current floor, current travel direction, and pending passenger hall requests.
   - Handles directional persistence, directional reversals when requests only exist in the opposing direction, and transitions to idle when no pending calls exist.
2. **`door_action(load_kg, blocked, emergency)`**:
   - Manages elevator door safety states based on sensor inputs:
     - High-priority emergency trigger (`"hold_open"`).
     - Weight limit threshold check at 630 kg (`"overload"`).
     - Optical/mechanical door edge obstruction sensor (`"reopen"`).
     - Standard safe closure (`"close"`).
3. **`pick_elevator(cars, floor)`**:
   - Allocates the most suitable car from a fleet `cars` (list of `(name, position, is_idle)` tuples) for a hall call at `floor`.
   - Calculates distance `gap = abs(position - floor)` and penalizes non-idle cars by +5 floors equivalent distance.
   - Deterministically picks the closest car, breaking ties in favor of the first evaluated car.

---

## 4. Difference Between Line Coverage and Branch Coverage

| Metric | Definition | Limitation |
| :--- | :--- | :--- |
| **Line Coverage** | Measures the percentage of executable lines of code that were executed at least once during test execution. | Can produce a false sense of security. A line may execute because a single condition was met, while alternate branch paths (e.g. `else` clauses, unexercised boolean evaluations) remain completely untested. |
| **Branch Coverage** | Measures whether every decision point / conditional branch (e.g., `if`, `while`, boolean compound expressions) evaluated to both **TRUE** and **FALSE**. | Requires tests to exercise every path through a decision structure, exposing hidden logical bugs and boundary edge cases that simple line execution overlooks. |

---

## 5. Testing Methodology

### A. Code Coverage Testing Methodology
- **Goal:** Execute 100% of the 39 executable statements in `elevator_dispatch.py`.
- **Approach:**
  - Systematically trigger each function block with valid inputs, extreme values, and boundary values.
  - Exercise normal passenger load states, emergency situations, elevator movements, and car selection scenarios.
  - Exclude test harness files from coverage metrics using `.coveragerc` so that metrics reflect the production application accurately.

### B. Branch Coverage Testing Methodology
- **Goal:** Exercise both `True` and `False` outcomes for all 28 decision branches in `elevator_dispatch.py`.
- **Approach:**
  - Construct a comprehensive decision truth table covering all permutations of `direction` (`"up"`, `"down"`, `"idle"`, unknown) and `above`/`below` request partitions.
  - Test door action condition priority: emergency override (True/False), load limit boundary (630 kg vs 631 kg), obstruction sensor (True/False).
  - Test car fleet loops: 0 iterations (empty list), 1 iteration (idle vs busy), multiple iterations (closer car replaces farther, farther car does not replace, tie gap preserves earlier car).

---

## 6. Test Cases Implemented

### A. Code Coverage Test Suite (`CodeCoverageTest_elevator_dispatch_application.py`)
- **Total Tests:** 21 test cases (100% passing)
  - `test_next_direction_up_with_above_requests`: Up direction continuing up.
  - `test_next_direction_up_with_below_requests_only`: Up direction reversing to down.
  - `test_next_direction_up_with_no_remaining_requests`: Up direction becoming idle.
  - `test_next_direction_down_with_below_requests`: Down direction continuing down.
  - `test_next_direction_down_with_above_requests_only`: Down direction reversing to up.
  - `test_next_direction_down_with_no_remaining_requests`: Down direction becoming idle.
  - `test_next_direction_idle_with_above_requests`: Idle state picking up.
  - `test_next_direction_idle_with_below_requests_only`: Idle state picking down.
  - `test_next_direction_idle_with_no_requests`: Idle state remaining idle.
  - `test_next_direction_unknown_direction_with_requests`: Fallthrough from invalid direction strings.
  - `test_door_action_emergency_overrides_everything`: Emergency priority over weight and obstruction.
  - `test_door_action_overload_normal`: Weight > 630 kg triggers overload.
  - `test_door_action_blocked_normal`: Obstruction triggers door reopening.
  - `test_door_action_normal_close`: Safe nominal conditions close doors.
  - `test_door_action_boundary_weight_630`: Threshold boundary checks (630 vs 631 kg).
  - `test_pick_elevator_empty_fleet`: Empty fleet returns None.
  - `test_pick_elevator_single_idle_car`: Single idle car selected.
  - `test_pick_elevator_single_busy_car`: Single busy car selected with +5 penalty.
  - `test_pick_elevator_multiple_cars_idle_closer`: Closer idle car chosen over farther idle car.
  - `test_pick_elevator_penalty_causes_farther_idle_to_win`: Penalty allows idle farther car to defeat busy closer car.
  - `test_pick_elevator_tie_preserves_first`: Tied distances preserve the first registered car.

### B. Branch Coverage Test Suite (`BranchCoverageTest_elevator_dispatch_application.py`)
- **Total Tests:** 20 test cases structured into 3 test classes (100% passing)
  - `TestNextDirectionBranchCoverage`: 9 tests exercising all branches of direction evaluation (`direction == "up"`, `direction == "down"`, other directions, `above` True/False, `below` True/False, empty/same-floor requests).
  - `TestDoorActionBranchCoverage`: 4 tests exercising full truth table of `emergency`, `load_kg > 630`, and `blocked`.
  - `TestPickElevatorBranchCoverage`: 7 tests exercising empty loop (0 iterations), single car (idle True/False), multiple cars (`gap < best_gap` True/False), tied gap evaluation, and penalty reversal.

---

## 7. Execution Commands

### Running Code Coverage
```bash
cd "lab6 soln"
coverage run -m pytest CodeCoverageTest_elevator_dispatch_application.py
coverage report -m
```

### Running Branch Coverage
```bash
cd "lab6 soln"
coverage run --branch -m pytest BranchCoverageTest_elevator_dispatch_application.py
coverage report -m
```

---

## 8. Actual Coverage Results

### A. Statement (Line) Coverage
- **Total Statements:** 39
- **Missed Statements:** 0
- **Line Coverage Percentage:** **100%** (Requirement: Minimum 90%)
- **Test Results:** 21 passed in 0.54s

```
Name                                                                           Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------------------------------
D:\Sem 5\SE Lab\Lab_6_7\L6_L7_38_elevator_dispatch\lab6\elevator_dispatch.py      39      0   100%
------------------------------------------------------------------------------------------------------------
TOTAL                                                                             39      0   100%
```

### B. Branch Coverage
- **Total Statements:** 39
- **Missed Statements:** 0
- **Total Branches:** 28
- **Partial Branches (BrPart):** 0
- **Missing Branches:** 0
- **Branch Coverage Percentage:** **100%** (Requirement: Minimum 90%)
- **Test Results:** 20 passed in 0.55s

```
Name                                                                           Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------------------------------------------
D:\Sem 5\SE Lab\Lab_6_7\L6_L7_38_elevator_dispatch\lab6\elevator_dispatch.py      39      0     28      0   100%
--------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                             39      0     28      0   100%
```

---

## 9. Screenshots and Evidence Locations
All evidence files are located inside `lab6 soln/evidence/`:
1. **Code Coverage Screenshot:** `evidence/code_coverage.png` (Terminal output showing 21 passed tests and 100% coverage)
2. **Branch Coverage Screenshot:** `evidence/branch_coverage.png` (Terminal output showing 20 passed tests, 28/28 branches and 100% coverage)
3. **Code Coverage Text Output:** `evidence/code_coverage.txt`
4. **Branch Coverage Text Output:** `evidence/branch_coverage.txt`

*(Note: In accordance with the Lab 6 handout and instructions, a PDF document is not required for Lab 6).*

---

## 10. Conclusion
By applying systematic code and branch coverage analysis using `coverage.py` and `pytest`:
- All 39 executable statements and all 28 decision branches in `elevator_dispatch.py` were fully exercised and verified.
- Edge cases including boundary load thresholds (630 kg vs 631 kg), tied dispatch gaps, busy car penalties, and directional reversals were completely validated.
- 100% code coverage and 100% branch coverage were achieved, exceeding the required 90% threshold.
