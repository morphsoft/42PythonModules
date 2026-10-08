def secure_archive(file_name: str, action: str = "read",
                   content: str = "") -> tuple[bool, str]:
    """Safely read from or write to a file using a context manager.

    Returns (True, data) on success, where data is the file's contents
    for a read or a confirmation message for a write, and
    (False, error_message) on failure.
    """
    try:
        if action == "read":
            with open(file_name) as archive:
                return (True, archive.read())
        if action == "write":
            with open(file_name, "w") as archive:
                archive.write(content)
            return (True, "Content successfully written to file")
        return (False, f"Unknown action '{action}'")
    except (OSError, ValueError) as error:
        return (False, str(error))


def main() -> None:
    """Demonstrate secure_archive on several files."""
    print("=== Cyber Archives Security ===")
    print()
    print("Using 'secure_archive' to read from a nonexistent file:")
    print(secure_archive("/not/existing/file"))
    print()
    print("Using 'secure_archive' to read from an inaccessible file:")
    print(secure_archive("/etc/master.passwd"))
    print()
    print("Using 'secure_archive' to read from a regular file:")
    success, content = secure_archive("ancient_fragment.txt")
    print((success, content))
    print()
    print("Using 'secure_archive' to write previous content to a new file:")
    if success:
        print(secure_archive("new_fragment.txt", "write", content))
    else:
        print("Nothing to write, the previous read failed.")


if __name__ == "__main__":
    main()
