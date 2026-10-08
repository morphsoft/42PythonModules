import importlib
import importlib.metadata
import sys
from typing import Any

DEPENDENCIES = {
    "pandas": "Data manipulation",
    "numpy": "Numerical computation",
    "matplotlib": "Visualization",
}

DATA_POINTS = 1000
OUTPUT_FILE = "matrix_analysis.png"


def check_dependencies() -> tuple[dict[str, Any], list[str]]:
    """Import each dependency, report its version, collect the missing."""
    print("Checking dependencies:")
    modules: dict[str, Any] = {}
    missing: list[str] = []
    for name, purpose in DEPENDENCIES.items():
        try:
            modules[name] = importlib.import_module(name)
            version = importlib.metadata.version(name)
            print(f"[OK] {name} ({version}) - {purpose} ready")
        except ImportError:
            print(f"[MISSING] {name} - {purpose} unavailable")
            missing.append(name)
        except importlib.metadata.PackageNotFoundError:
            print(f"[OK] {name} (unknown version) - {purpose} ready")
    return modules, missing


def print_install_instructions(missing: list[str]) -> None:
    """Tell the user how to load the missing programs."""
    print()
    print(f"Missing programs: {', '.join(missing)}")
    print("Load them into your environment with one of:")
    print("  pip:    pip install -r requirements.txt")
    print("  Poetry: poetry install  (then: poetry run python loading.py)")


def compare_package_managers() -> None:
    """Show installed versions and how pip and Poetry differ."""
    print()
    print("Package manager comparison:")
    print(f"{'Package':<12}{'Installed':<12}pip source       Poetry source")
    for name in DEPENDENCIES:
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version = "-"
        print(f"{name:<12}{version:<12}requirements.txt pyproject.toml")
    print()
    print("pip:    installs what requirements.txt lists, into whatever")
    print("        environment is active; you manage the venv yourself.")
    print("Poetry: reads pyproject.toml, resolves versions into")
    print("        poetry.lock and creates/uses its own venv.")
    for tool in ("pip", "poetry"):
        try:
            print(f"{tool} version: {importlib.metadata.version(tool)}")
        except importlib.metadata.PackageNotFoundError:
            print(f"{tool} version: not installed in this environment")


def analyze_matrix_data(modules: dict[str, Any]) -> None:
    """Simulate Matrix data with numpy, analyze with pandas, plot."""
    np = modules["numpy"]
    pd = modules["pandas"]
    matplotlib = modules["matplotlib"]
    matplotlib.use("Agg")
    plt = importlib.import_module("matplotlib.pyplot")

    print()
    print("Analyzing Matrix data...")
    rng = np.random.default_rng(seed=42)
    signal = rng.normal(loc=0.0, scale=1.0, size=DATA_POINTS).cumsum()
    noise = rng.normal(loc=0.0, scale=0.5, size=DATA_POINTS)
    frame = pd.DataFrame({"signal": signal, "noise": noise})
    frame["observed"] = frame["signal"] + frame["noise"]
    print(f"Processing {len(frame)} data points...")
    print(f"Mean observed value: {frame['observed'].mean():.3f}")
    print(f"Std observed value:  {frame['observed'].std():.3f}")
    print(f"Peak observed value: {frame['observed'].max():.3f}")

    print("Generating visualization...")
    plt.figure(figsize=(10, 4))
    plt.plot(frame.index, frame["observed"], color="green", linewidth=0.8,
             label="observed")
    plt.plot(frame.index, frame["signal"], color="black", linewidth=1.2,
             label="signal")
    plt.title("Matrix data stream")
    plt.xlabel("tick")
    plt.ylabel("value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    plt.close()


def main() -> int:
    """Load programs, compare managers, run the analysis."""
    print("LOADING STATUS: Loading programs...")
    print()
    modules, missing = check_dependencies()
    compare_package_managers()
    if len(missing) > 0:
        print_install_instructions(missing)
        return 1
    try:
        analyze_matrix_data(modules)
    except (ValueError, OSError, AttributeError) as error:
        print(f"Analysis failed: {error}")
        return 1
    print()
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
