def input_temperature(temp_str):
    try:
        temperature = int(temp_str)
    except ValueError:
        print("Error: Invalid temperature input.")
        return None
    if (temperature == None):
        raise ValueError("Error: Temperature input is required.")
    return temperature

def test_temperature():
    test_cases = ["25", "abc"]
    for temp_str in test_cases:
        try:
            result = input_temperature(temp_str)
            print(f"Input: {temp_str}, Output: {result}")
        except ValueError as e:
            print(f"Input: {temp_str}, Exception: {e}")