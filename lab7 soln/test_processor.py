import sys
import os
import pytest
from hypothesis import given, strategies as st, assume

# Import functions under test
from processor import parse_request, total_travel, load_percent


# =====================================================================
# 1. FUZZING FOR parse_request
# =====================================================================

@given(st.text() | st.none())
def test_parse_request_no_crash(s):
    """Function must never crash on arbitrary text or None."""
    try:
        parse_request(s)
    except Exception as e:
        assert False, f"parse_request crashed with: {type(e).__name__}: {e}"


@given(st.one_of(st.integers(), st.booleans(), st.lists(st.integers()), st.floats()))
def test_parse_request_invalid_types_no_crash(x):
    """Function must safely reject non-string types without crashing."""
    try:
        res = parse_request(x)
        assert res is None
    except Exception as e:
        assert False, f"parse_request crashed on invalid type {type(x)} with {type(e).__name__}: {e}"


@given(
    start=st.integers(min_value=-100000, max_value=100000),
    end=st.integers(min_value=-100000, max_value=100000),
    spaces1=st.text(alphabet=" \t", max_size=3),
    spaces2=st.text(alphabet=" \t", max_size=3),
)
def test_parse_request_valid_property(start, end, spaces1, spaces2):
    """Valid 'START->END' string must correctly parse to tuple of (int, int)."""
    text = f"{spaces1}{start}{spaces2}->{spaces1}{end}{spaces2}"
    result = parse_request(text)
    assert result == (start, end), f"Expected {(start, end)}, got {result}"


@given(st.text())
def test_parse_request_malformed_returns_none(s):
    """Any string without exactly one '->' with valid integers must return None."""
    # Exclude strings that happen to be valid START->END with integer start and end
    if "->" in s:
        parts = s.split("->")
        if len(parts) == 2:
            try:
                int(parts[0].strip())
                int(parts[1].strip())
                assume(False)  # valid input, skip this test case
            except ValueError:
                pass
    try:
        res = parse_request(s)
        assert res is None
    except Exception as e:
        assert False, f"parse_request crashed on malformed string: {type(e).__name__}: {e}"


# =====================================================================
# 2. FUZZING FOR total_travel
# =====================================================================

@given(st.text() | st.none())
def test_total_travel_no_crash(s):
    """Function must never crash on arbitrary text or None."""
    try:
        total_travel(s)
    except Exception as e:
        assert False, f"total_travel crashed with: {type(e).__name__}: {e}"


@given(st.one_of(st.integers(), st.booleans(), st.lists(st.integers()), st.floats()))
def test_total_travel_invalid_types_no_crash(x):
    """Function must safely handle non-string types without crashing."""
    try:
        res = total_travel(x)
        assert res == 0
    except Exception as e:
        assert False, f"total_travel crashed on non-string type {type(x)} with {type(e).__name__}: {e}"


@given(st.lists(st.integers(min_value=-500, max_value=500), min_size=0, max_size=30))
def test_total_travel_valid_property(floors):
    """For any list of integer floors, total_travel computes sum of consecutive distances."""
    csv_str = ",".join(str(f) for f in floors)
    result = total_travel(csv_str)
    
    if len(floors) < 2:
        expected = 0
    else:
        expected = sum(abs(floors[i + 1] - floors[i]) for i in range(len(floors) - 1))
    
    assert result == expected
    assert result >= 0, "Total travel distance must always be non-negative"


@given(st.lists(st.integers(min_value=-500, max_value=500), min_size=2, max_size=20))
def test_total_travel_reversal_symmetry(floors):
    """Property: Travel distance is symmetric whether visiting forward or in reverse."""
    forward_csv = ",".join(str(f) for f in floors)
    reverse_csv = ",".join(str(f) for f in reversed(floors))
    assert total_travel(forward_csv) == total_travel(reverse_csv)


@given(st.lists(st.integers(min_value=-500, max_value=500), min_size=2, max_size=20))
def test_total_travel_triangle_inequality(floors):
    """Property: Total path distance is always >= direct displacement between start and end."""
    csv_str = ",".join(str(f) for f in floors)
    total_dist = total_travel(csv_str)
    direct_dist = abs(floors[-1] - floors[0])
    assert total_dist >= direct_dist


# =====================================================================
# 3. FUZZING FOR load_percent
# =====================================================================

@given(st.text() | st.none())
def test_load_percent_no_crash(s):
    """Function must never crash on arbitrary text or None."""
    try:
        load_percent(s)
    except Exception as e:
        assert False, f"load_percent crashed with: {type(e).__name__}: {e}"


@given(st.one_of(st.integers(), st.booleans(), st.lists(st.integers()), st.floats()))
def test_load_percent_invalid_types_no_crash(x):
    """Function must safely handle non-string types without crashing."""
    try:
        res = load_percent(x)
        assert res is None
    except Exception as e:
        assert False, f"load_percent crashed on non-string type {type(x)} with {type(e).__name__}: {e}"


@given(
    load=st.integers(min_value=0, max_value=100000),
    capacity=st.integers(min_value=1, max_value=100000),
)
def test_load_percent_valid_property(load, capacity):
    """For valid non-negative load and strictly positive capacity, computes integer load percentage."""
    text = f"{load} of {capacity}"
    expected = (load * 100) // capacity
    assert load_percent(text) == expected


@given(
    load=st.integers(min_value=0, max_value=10000),
    capacity=st.integers(max_value=0),  # zero and negative capacity
)
def test_load_percent_zero_or_negative_capacity_no_crash(load, capacity):
    """Capacity <= 0 is physically invalid; must not crash with ZeroDivisionError."""
    text = f"{load} of {capacity}"
    try:
        res = load_percent(text)
        assert res is None, f"Expected None for invalid capacity <= 0, got {res}"
    except Exception as e:
        assert False, f"load_percent crashed with {type(e).__name__}: {e}"


@given(
    load=st.integers(max_value=-1),  # negative load
    capacity=st.integers(min_value=1, max_value=10000),
)
def test_load_percent_negative_load_no_crash(load, capacity):
    """Negative load is physically invalid; must not crash and should return None."""
    text = f"{load} of {capacity}"
    try:
        res = load_percent(text)
        assert res is None, f"Expected None for negative load, got {res}"
    except Exception as e:
        assert False, f"load_percent crashed with {type(e).__name__}: {e}"
