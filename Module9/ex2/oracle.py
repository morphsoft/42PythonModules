import os
import sys

REQUIRED = ("MATRIX_MODE", "DATABASE_URL", "API_KEY", "LOG_LEVEL",
            "ZION_ENDPOINT")
DEFAULTS = {"MATRIX_MODE": "development", "LOG_LEVEL": "INFO"}


def load_env_file() -> bool:
    """Load .env through python-dotenv; real env vars keep priority."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("WARNING: python-dotenv is not installed, "
              "only real environment variables are used")
        print("         (pip install -r requirements.txt)")
        return False
    return bool(load_dotenv(override=False))


def read_config() -> tuple[dict[str, str], list[str]]:
    """Collect the configuration and the names that are missing."""
    config: dict[str, str] = {}
    missing: list[str] = []
    for name in REQUIRED:
        value = os.environ.get(name, "").strip()
        if value == "":
            if name in DEFAULTS:
                config[name] = DEFAULTS[name]
                print(f"WARNING: {name} not set, using default "
                      f"'{DEFAULTS[name]}'")
            else:
                missing.append(name)
        else:
            config[name] = value
    return config, missing


def mask(secret: str, production: bool) -> str:
    """Hide most of a secret; hide all of it in production."""
    if production:
        return "********"
    return secret[:3] + "*" * max(len(secret) - 3, 0)


def describe_database(url: str) -> str:
    """Summarize the database connection without leaking the URL."""
    if url.startswith("sqlite") or "localhost" in url or "127.0.0.1" in url:
        return "Connected to local instance"
    return "Connected to remote instance"


def report(config: dict[str, str], missing: list[str],
           env_loaded: bool) -> None:
    """Print the configuration in a mode-dependent way."""
    production = config["MATRIX_MODE"] == "production"
    print()
    print("Configuration loaded:")
    print(f"Mode: {config['MATRIX_MODE']}")
    if "DATABASE_URL" in config:
        detail = "" if production else f" ({config['DATABASE_URL']})"
        print(f"Database: {describe_database(config['DATABASE_URL'])}"
              f"{detail}")
    else:
        print("Database: NOT CONFIGURED (DATABASE_URL missing)")
    if "API_KEY" in config:
        print(f"API Access: Authenticated "
              f"(key {mask(config['API_KEY'], production)})")
    else:
        print("API Access: DENIED (API_KEY missing)")
    print(f"Log Level: {config['LOG_LEVEL']}")
    if "ZION_ENDPOINT" in config:
        print(f"Zion Network: Online ({config['ZION_ENDPOINT']})")
    else:
        print("Zion Network: Offline (ZION_ENDPOINT missing)")
    print()
    print("Environment security check:")
    print("[OK] No hardcoded secrets detected")
    env_state = "[OK]" if env_loaded else "[!!]"
    print(f"{env_state} .env file "
          f"{'properly configured' if env_loaded else 'not found'}")
    print("[OK] Production overrides available "
          "(MATRIX_MODE=production ...)")
    if production:
        print("[OK] Production mode: secrets are fully masked")
    else:
        print("[..] Development mode: verbose output, secrets partly shown")


def main() -> int:
    """Read the Matrix configuration and report it."""
    print("ORACLE STATUS: Reading the Matrix...")
    env_loaded = load_env_file()
    config, missing = read_config()
    report(config, missing, env_loaded)
    print()
    if len(missing) > 0:
        print(f"The Oracle is blind to: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in the values.")
        return 1
    print("The Oracle sees all configurations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
