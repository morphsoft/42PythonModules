def garden_operations(operation_number: int) -> None:
    """Run a faulty operation depending on operation_number (0-3)."""
    if operation_number == 0:
        int("abc")
    elif operation_number == 1:
        10 / 0
    elif operation_number == 2:
        open("/non/existent/file")
    elif operation_number == 3:
        "plants: " + 5
    return


def test_error_types() -> None:
    print("=== Garden Error Types Demo ===")

    # Each error type caught by its own except clause
    for operation_number in [0, 1, 2, 3, 4]:
        print(f"Testing operation {operation_number}...")
        try:
            garden_operations(operation_number)
            print("Operation completed successfully")
        except ValueError as error:
            print(f"Caught ValueError: {error}")
        except ZeroDivisionError as error:
            print(f"Caught ZeroDivisionError: {error}")
        except FileNotFoundError as error:
            print(f"Caught FileNotFoundError: {error}")
        except TypeError as error:
            print(f"Caught TypeError: {error}")

    # Several error types caught by a single except clause
    print("\nTesting multiple errors with one try block...")
    for operation_number in [0, 1, 2, 3]:
        try:
            garden_operations(operation_number)
        except (ValueError, ZeroDivisionError,
                FileNotFoundError, TypeError) as error:
            print(f"Caught an error, but program continues: {error}")

    print("\nAll error types tested successfully!")


if __name__ == "__main__":
    test_error_types()
