# Lab 7: Fuzz Testing for Input Validation Bugs

## 1. Student Details
- **Student Name:** Anish A Kunder
- **SRN:** PES1UG24AM343
- **Repository:** https://github.com/planetai05/L6_L7_38_elevator_dispatch
- **Branch:** `lab6-lab7-solutions`

---

## 2. Lab Title & Objective
**Title:** Lab 7: Fuzz Testing for Input Validation Bugs  
**Objective:**
- Explore property-based fuzz testing as an automated security and quality assurance methodology using Python's **Hypothesis** framework.
- Detect hidden edge-case crashes, boundary exceptions, and data type vulnerabilities in the elevator dispatch software.
- Analyze automatic counterexample shrinking performed by Hypothesis.
- Defensively harden the software against arbitrary, malformed, and unexpected inputs without relying on blanket exception handling (`try...except Exception`).
- Formally verify mathematical and physical invariants across thousands of generated test inputs.

---

## 3. Application Description
The application under test (`processor.py` / `elevator_dispatch.py`) processes user and sensor inputs for an elevator dispatch controller:
- Parsing passenger trip requests from text format.
- Calculating cumulative travel between visited floors from CSV strings.
- Computing percentage car load from weight telemetry.

The original application assumed ideal inputs and lacked type checks, boundary validation, and error guards, making it susceptible to crashes and invalid outputs.

---

## 4. Description of All Three Functions

### 1. `parse_request(text)`
- **Expected Behavior:** Parses an elevator request string in the format `'START->END'` (e.g. `'5->9'`) and returns a tuple of two integers `(start, end)`.
- **Defensive Safeguards:** Rejects non-strings, `None`, missing or duplicate `'->'` delimiters, and non-integer tokens by safely returning `None`.

### 2. `total_travel(floors_csv)`
- **Expected Behavior:** Parses a comma-separated list of floor numbers (e.g. `'1,5,3,9'`) and computes the cumulative absolute travel distance:
  $$\text{Total Travel} = \sum_{i=0}^{n-2} |\text{floor}_{i+1} - \text{floor}_i|$$
- **Defensive Safeguards:** Validates string type and non-empty status; ensures all comma-separated tokens are valid integers; returns `0` for empty inputs, single floors, or malformed tokens. Always returns an integer $\ge 0$.

### 3. `load_percent(text)`
- **Expected Behavior:** Parses load telemetry formatted as `'LOAD of CAPACITY'` (e.g. `'450 of 630'`) and computes integer load percentage:
  $$\text{Load Percent} = \lfloor \frac{\text{load} \times 100}{\text{capacity}} \rfloor$$
- **Defensive Safeguards:** Enforces strict binary split on `' of '`; checks integer values; enforces physical domain rules: $\text{capacity} > 0$ (preventing `ZeroDivisionError`) and $\text{load} \ge 0$ (preventing negative percentages); returns `None` for invalid inputs.

---

## 5. Hypothesis Testing Methodology
Property-based testing with **Hypothesis** tests system invariants across infinite, randomized input spaces rather than isolated hard-coded examples:
1. **Property Invariants:** Tests verify high-level properties that must hold true for all valid inputs:
   - *Round-Trip Property:* `parse_request(f"{a}->{b}") == (a, b)` for any integers $a, b$.
   - *Travel Invariance & Non-Negativity:* `total_travel(floors) >= 0` and `total_travel(floors) == total_travel(reversed(floors))`.
   - *Triangle Inequality:* Total path distance $\ge$ direct displacement $|\text{end} - \text{start}|$.
   - *Ratio Consistency:* `load_percent(f"{l} of {c}") == (l * 100) // c` for $l \ge 0, c > 0$.
2. **Crash Resilience:** Tests verify that arbitrary Unicode strings, `None`, or foreign data types never cause unhandled exceptions.
3. **Automated Shrinking:** When a failure occurs, Hypothesis systematically reduces the failing example to the smallest reproducer.

---

## 6. Hypothesis Strategies Used
- `st.text()`: Synthesizes arbitrary Unicode characters, empty strings, emojis, null bytes (`\x00`), and whitespace.
- `st.none()`: Fuzzes `None` references to verify null-safety.
- `st.integers()`: Generates arbitrary integers, negative bounds, zero, and extreme values ($\pm 10^5$).
- `st.lists(st.integers())`: Generates variable-length lists of floors (0 to 30 elements).
- `st.one_of(...)`: Injects foreign types (booleans, floats, lists) to verify defensive type guards.

---

## 7. Original Failures: 10 Failed, 4 Passed
When the property-based test suite was executed against the original unhardened application, Hypothesis uncovered **10 test failures and 4 passes** in 0.99 seconds:
```
=========================== short test summary info ===========================
FAILED test_processor.py::test_parse_request_no_crash - ExceptionGroup: Hypothesis found 3 distinct failures.
FAILED test_processor.py::test_parse_request_invalid_types_no_crash - AssertionError
FAILED test_processor.py::test_parse_request_malformed_returns_none - ExceptionGroup
FAILED test_processor.py::test_total_travel_no_crash - ExceptionGroup: Hypothesis found 2 distinct failures.
FAILED test_processor.py::test_total_travel_invalid_types_no_crash - AssertionError
FAILED test_processor.py::test_total_travel_valid_property - ValueError: invalid literal for int() with base 10: ''
FAILED test_processor.py::test_load_percent_no_crash - ExceptionGroup: Hypothesis found 2 distinct failures.
FAILED test_processor.py::test_load_percent_invalid_types_no_crash - AssertionError
FAILED test_processor.py::test_load_percent_zero_or_negative_capacity_no_crash - ZeroDivisionError / AssertionError
FAILED test_processor.py::test_load_percent_negative_load_no_crash - AssertionError: Expected None for negative load
======================== 10 failed, 4 passed in 0.99s =========================
```

---

## 8. Bugs Discovered
Hypothesis automatically shrunk counterexamples down to minimal reproducers:

| # | Function | Minimal Shrunk Input | Observed Exception / Failure | Root Cause Analysis |
|---|---|---|---|---|
| 1 | `parse_request` | `None`, `0` | `AttributeError: 'NoneType' object has no attribute 'split'` | No string type check before calling `.split()` |
| 2 | `parse_request` | `""` | `ValueError: not enough values to unpack (expected 2, got 1)` | Missing delimiter check before tuple unpacking |
| 3 | `parse_request` | `"->"` | `ValueError: invalid literal for int() with base 10: ''` | Splitting produces empty string tokens |
| 4 | `total_travel` | `None`, `0` | `AttributeError: 'NoneType' object has no attribute 'split'` | Missing string type check |
| 5 | `total_travel` | `""` | `ValueError: invalid literal for int() with base 10: ''` | Empty string yields `['']`, which fails `int('')` |
| 6 | `total_travel` | `","`, `"1,,3"` | `ValueError: invalid literal for int() with base 10: ''` | Missing empty/whitespace token validation |
| 7 | `load_percent` | `None`, `[1]` | `AttributeError: 'NoneType' object has no attribute 'split'` | Foreign types lack `.split()` method |
| 8 | `load_percent` | `""` | `ValueError: not enough values to unpack (expected 2, got 1)` | Absence of `' of '` delimiter causes unpacking crash |
| 9 | `load_percent` | `"10 of 0"` | `ZeroDivisionError: integer division or modulo by zero` | Zero elevator capacity unhandled |
| 10 | `load_percent` | `"-10 of 100"` | Logic Violation: produces `-10%` | Negative passenger load permitted without validation |

---

## 9. Fixes Implemented
All 10 defects were resolved in `lab7 soln/processor.py` through disciplined defensive programming:
1. **Explicit Integer Helper (`_is_integer`)**:
   - Validates that a string is non-empty, contains an optional leading `+` or `-`, and contains strictly digit characters without raising uncaught exceptions.
2. **Type and Null Guards**:
   - `isinstance(..., str)` checks at function entry points return safe fallbacks (`None` or `0`).
3. **Strict Delimiter Verification**:
   - Checks that `"->"` or `" of "` occurs exactly once before splitting.
4. **Physical Domain Validation**:
   - Enforces `capacity > 0` (preventing `ZeroDivisionError`) and `load >= 0`.
5. **Robust Token Processing**:
   - Strips whitespace from tokens and verifies every element in CSV strings.
6. **No Blanket Exception Handling**:
   - Programmatic validation avoids masking unexpected system faults.

---

## 10. Final Result: 14 Passed
Re-running the complete Hypothesis fuzz test suite against `processor.py`:
- **Total Tests:** 14 property-based tests
- **Passing Tests:** **14 passed, 0 failed in 1.28s** (100% passing rate)
- **Status:** All properties verified across thousands of synthesized inputs.

```
test_processor.py::test_parse_request_no_crash PASSED                    [  7%]
test_processor.py::test_parse_request_invalid_types_no_crash PASSED      [ 14%]
test_processor.py::test_parse_request_valid_property PASSED              [ 21%]
test_processor.py::test_parse_request_malformed_returns_none PASSED      [ 28%]
test_processor.py::test_total_travel_no_crash PASSED                     [ 35%]
test_processor.py::test_total_travel_invalid_types_no_crash PASSED       [ 42%]
test_processor.py::test_total_travel_valid_property PASSED               [ 50%]
test_processor.py::test_total_travel_reversal_symmetry PASSED            [ 57%]
test_processor.py::test_total_travel_triangle_inequality PASSED          [ 64%]
test_processor.py::test_load_percent_no_crash PASSED                     [ 71%]
test_processor.py::test_load_percent_invalid_types_no_crash PASSED       [ 78%]
test_processor.py::test_load_percent_valid_property PASSED               [ 85%]
test_processor.py::test_load_percent_zero_or_negative_capacity_no_crash PASSED [ 92%]
test_processor.py::test_load_percent_negative_load_no_crash PASSED       [100%]

============================= 14 passed in 1.28s ==============================
```

---

## 11. Commands Required to Reproduce Results

### 1. Run Original Application
```bash
cd "lab7"
python elevator_dispatch.py
```

### 2. Run Initial Hypothesis Tests (Failing)
```bash
cd "lab7 soln"
python -m pytest test_processor.py
```

### 3. Run Fixed Application
```bash
cd "lab7 soln"
python processor.py
```

### 4. Run Final Hypothesis Tests (Passing)
```bash
cd "lab7 soln"
python -m pytest test_processor.py -v
```

---

## 12. Evidence Folder Structure
All evidence artifacts are maintained in `lab7 soln/evidence/`:
```
lab7 soln/evidence/
├── initial_processor_output.png    # Screenshot: Original application interactive run
├── hypothesis_failing_tests.png    # Screenshot: 10 failed, 4 passed Hypothesis run
├── fixed_processor_output.png      # Screenshot: Fixed application interactive run
├── hypothesis_passing_tests.png    # Screenshot: 14 passed Hypothesis run
├── initial_processor_output.txt    # Terminal log of original execution
├── hypothesis_failing_tests.txt    # Terminal log with full Hypothesis tracebacks
├── fixed_processor_output.txt      # Terminal log of fixed execution
└── hypothesis_passing_tests.txt    # Terminal log of 14 passed tests
```

---

## 13. PDF Location
The official laboratory report PDF is generated and saved at:
- **`lab7 soln/Lab7_FuzzTesting_Evidence.pdf`**

This 5-page document includes the student cover page, theoretical introduction, function specifications, Hypothesis methodology, bug analysis table, defensive fixes, and all four genuine terminal screenshots with descriptive captions.

---

## 14. Conclusion
Property-based fuzz testing with Hypothesis exposed critical real-world vulnerabilities—including null dereferences, literal parsing crashes, zero division, and domain logic errors—that simple unit tests failed to anticipate. Through disciplined defensive input validation, type guarding, and boundary checks, the elevator dispatch system was transformed into a resilient, crash-proof module meeting rigorous software engineering standards.
