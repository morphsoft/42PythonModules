import sys
import typing


def recover_file(file_name: str) -> str | None:
    """Open a file, display its contents, close it and return them."""
    print(f"Accessing file '{file_name}'")
    try:
        archive: typing.IO[str] = open(file_name)
    except OSError as error:
        print(f"Error opening file '{file_name}': {error}")
        return None
    content = None
    try:
        content = archive.read()
        print("---")
        print()
        print(content)
        print("---")
    except (OSError, ValueError) as error:
        print(f"Error reading file '{file_name}': {error}")
    finally:
        archive.close()
        print(f"File '{file_name}' closed.")
    return content


def transform_data(content: str) -> str:
    """Add the archive character '#' at the end of each line."""
    new_content = ""
    for line in content.splitlines():
        new_content += line + "#\n"
    return new_content


def save_file(file_name: str, content: str) -> None:
    """Create or replace the file with the given content."""
    print(f"Saving data to '{file_name}'")
    try:
        archive: typing.IO[str] = open(file_name, "w")
    except OSError as error:
        print(f"Error opening file '{file_name}': {error}")
        print("Data not saved.")
        return
    try:
        archive.write(content)
        print(f"Data saved in file '{file_name}'.")
    except OSError as error:
        print(f"Error writing file '{file_name}': {error}")
        print("Data not saved.")
    finally:
        archive.close()


def ask_file_name() -> str:
    """Ask the user for a file name, empty when input is closed."""
    try:
        return input("Enter new file name (or empty): ")
    except EOFError:
        print()
        return ""


def main() -> None:
    """Recover a file, transform it and optionally save the result."""
    if len(sys.argv) != 2:
        print("Usage: ft_archive_creation.py <file>")
        return
    print("=== Cyber Archives Recovery & Preservation ===")
    content = recover_file(sys.argv[1])
    if content is None:
        return
    print()
    print("Transform data:")
    new_content = transform_data(content)
    print("---")
    print()
    print(new_content)
    print("---")
    file_name = ask_file_name()
    if file_name == "":
        print("Not saving data.")
        return
    save_file(file_name, new_content)


if __name__ == "__main__":
    main()
