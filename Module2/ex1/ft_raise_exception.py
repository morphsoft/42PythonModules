def input_temperature(temp_str):
    try:
        result = int(temp_str)
    except ValueError:
        print("Error: Invalid temperature input.")
        return None
    if (result is not None) and (result < 0):
        raise ValueError("Error: Temperature out of range (min is 0 degrees celsius).")
    if (result is not None) and (result > 40):
        raise ValueError("Error: Temperature out of range (max is 40 degrees celsius).")
    if (result is None):
        raise ValueError("Error: Temperature input is required.")
    return result

def test_temperature():
    test_cases = ["25", "-50", "100", "abc"]
    for temp_str in test_cases:
        try:
            result = input_temperature(temp_str)
            print(f"Input: {temp_str}, Output: {result}")
        except ValueError as e:
            print(f"Input: {temp_str}, Exception: {e}")