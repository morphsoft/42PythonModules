def garden_operations(operation_number: int) -> None:
    """Run a faulty operation depending on operation_number (0-3)."""
    if operation_number == 0:
        int("abc")
    elif operation_number == 1:
        10 / 0
    elif operation_number == 2:
        open("missing_garden_file.txt")
    elif operation_number == 3:
        "plants: " + 5
    return


def test_error_types() -> None:
    print("=== Garden Error Types Demo ===\n")

    # One try block, several separate except clauses
    for operation_number in range(5):
        print(f"Testing operation {operation_number}...")
        try:
            garden_operations(operation_number)
            print("Operation completed successfully")
        except ValueError as error:
            print(f"Caught ValueError: {error}")
            print("-> Bad data: the text could not be converted to a number")
        except ZeroDivisionError as error:
            print(f"Caught ZeroDivisionError: {error}")
            print("-> You cannot divide by zero")
        except FileNotFoundError as error:
            print(f"Caught FileNotFoundError: {error}")
            print("-> The file does not exist, so it was never opened")
        except TypeError as error:
            print(f"Caught TypeError: {error}")
            print("-> A string and a number cannot be added together")
        print("Program is still running!\n")

    print("Testing multiple errors together...")
    for operation_number in range(4):
        try:
            garden_operations(operation_number)
        except (ValueError, ZeroDivisionError,
                FileNotFoundError, TypeError) as error:
            print(f"Caught {type(error).__name__}, but program continues!")

    print("\nAll error types tested successfully!")


if __name__ == "__main__":
    test_error_types()