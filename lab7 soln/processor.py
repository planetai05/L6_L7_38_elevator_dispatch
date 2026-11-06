def _is_integer(s):
    """Helper to validate if a string represents an integer without blanket exceptions."""
    if not isinstance(s, str):
        return False
    s = s.strip()
    if not s:
        return False
    if s[0] in "+-":
        return len(s) > 1 and s[1:].isdigit()
    return s.isdigit()


def parse_request(text):
    """
    Parses an elevator request in the format 'START->END'.
    Returns a tuple of (start, end) as ints, or None if the input is invalid.
    """
    if not isinstance(text, str):
        return None
    
    # Must contain delimiter and split into exactly two parts
    if "->" not in text:
        return None
    parts = text.split("->")
    if len(parts) != 2:
        return None
    
    start_str = parts[0].strip()
    end_str = parts[1].strip()
    
    if not _is_integer(start_str) or not _is_integer(end_str):
        return None
    
    return int(start_str), int(end_str)


def total_travel(floors_csv):
    """
    Calculates total absolute floor distance traveled from a CSV of floor numbers.
    Returns integer total travel distance (>= 0).
    Returns 0 for empty, single-floor, or invalid inputs.
    """
    if not isinstance(floors_csv, str):
        return 0
    
    stripped = floors_csv.strip()
    if not stripped:
        return 0
    
    tokens = stripped.split(",")
    # All tokens must be valid integers; empty tokens like trailing comma mean invalid
    for token in tokens:
        if not _is_integer(token):
            return 0
    
    floors = [int(token.strip()) for token in tokens]
    if len(floors) < 2:
        return 0
    
    return sum(abs(floors[i + 1] - floors[i]) for i in range(len(floors) - 1))


def load_percent(text):
    """
    Calculates load percentage as an integer (load * 100 // capacity).
    Requires input in format 'LOAD of CAPACITY' with non-negative load and capacity > 0.
    Returns None for malformed inputs, non-strings, negative load, or capacity <= 0.
    """
    if not isinstance(text, str):
        return None
    
    if " of " not in text:
        return None
    parts = text.split(" of ")
    if len(parts) != 2:
        return None
    
    load_str = parts[0].strip()
    cap_str = parts[1].strip()
    
    if not _is_integer(load_str) or not _is_integer(cap_str):
        return None
    
    load = int(load_str)
    capacity = int(cap_str)
    
    # Physical validation: capacity must be strictly positive, load must be non-negative
    if capacity <= 0 or load < 0:
        return None
    
    return (load * 100) // capacity


def main():
    print("==== Running parse_request ====")
    user_input = input("Enter a request as FROM->TO (e.g. 5->9): ")
    result = parse_request(user_input)
    print("From and To:", result)

    print("\n==== Running total_travel ====")
    user_input = input("Enter floors visited as CSV (e.g. 1,5,3,9): ")
    result = total_travel(user_input)
    print("Floors Travelled:", result)

    print("\n==== Running load_percent ====")
    user_input = input("Enter load as 'X of Y' (e.g. 450 of 630): ")
    result = load_percent(user_input)
    print("Load Percent:", result)


if __name__ == "__main__":
    main()
