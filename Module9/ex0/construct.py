import os
import site
import sys


def in_virtual_env() -> bool:
    """A venv changes sys.prefix while sys.base_prefix stays global."""
    return (sys.prefix != sys.base_prefix
            or os.environ.get("VIRTUAL_ENV") is not None)


def site_packages_path() -> str:
    """Where pip installs packages for the running interpreter."""
    try:
        candidates = site.getsitepackages()
    except AttributeError:
        candidates = []
    for path in candidates:
        if path.endswith("site-packages"):
            return path
    if len(candidates) > 0:
        return candidates[0]
    return site.getusersitepackages()


def report_global() -> None:
    """Explain how to leave the global environment."""
    print("MATRIX STATUS: You're still plugged in")
    print()
    print(f"Current Python: {sys.executable}")
    print("Virtual Environment: None detected")
    print()
    print("WARNING: You're in the global environment!")
    print("The machines can see everything you install.")
    print()
    print("Global package installation path:")
    print(site_packages_path())
    print()
    print("To enter the construct, run:")
    print("python -m venv matrix_env")
    print("source matrix_env/bin/activate  # On Unix")
    print("matrix_env\\Scripts\\activate     # On Windows")
    print()
    print("Then run this program again.")


def report_virtual() -> None:
    """Describe the virtual environment currently active."""
    env_path = os.environ.get("VIRTUAL_ENV", sys.prefix)
    print("MATRIX STATUS: Welcome to the construct")
    print()
    print(f"Current Python: {sys.executable}")
    print(f"Virtual Environment: {os.path.basename(env_path)}")
    print(f"Environment Path: {env_path}")
    print()
    print("SUCCESS: You're in an isolated environment!")
    print("Safe to install packages without affecting")
    print("the global system.")
    print()
    print("Package installation path:")
    print(site_packages_path())
    print()
    print(f"Global Python left behind: {sys.base_prefix}")


def main() -> None:
    """Detect the environment and report accordingly."""
    try:
        if in_virtual_env():
            report_virtual()
        else:
            report_global()
    except OSError as error:
        print(f"Unable to inspect the environment: {error}")


if __name__ == "__main__":
    main()
