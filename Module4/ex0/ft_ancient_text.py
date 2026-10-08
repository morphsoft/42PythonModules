import sys
import typing


def recover_file(file_name: str) -> None:
    """Open a file, display its contents like cat, then close it."""
    print(f"Accessing file '{file_name}'")
    try:
        archive: typing.IO[str] = open(file_name)
    except OSError as error:
        print(f"Error opening file '{file_name}': {error}")
        return
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


def main() -> None:
    """Recover the file given as command-line parameter."""
    if len(sys.argv) != 2:
        print("Usage: ft_ancient_text.py <file>")
        return
    print("=== Cyber Archives Recovery ===")
    recover_file(sys.argv[1])


if __name__ == "__main__":
    main()
