import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "src" / "version.py"
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_JSON = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"


def load_app_version() -> str:
    match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', VERSION_FILE.read_text())
    if not match:
        sys.exit("APP_VERSION not found in src/version.py")
    return match.group(1)


def replace_versions(path: Path, version: str, substitutions: list[tuple[str, str]], label: str) -> None:
    text = path.read_text()
    new_text = text
    total = 0
    for pattern, context in substitutions:
        new_text, n = re.subn(pattern, rf'\g<1>"{version}"', new_text, count=1, flags=re.M)
        if n == 0:
            sys.exit(f"{context} not found in {path.name}")
        total += n
    if new_text != text:
        path.write_text(new_text)
        print(f"synced {label} version -> {version} ({total} field(s))")
    else:
        print(f"{label} already in sync")


def sync() -> None:
    version = load_app_version()

    replace_versions(
        PYPROJECT,
        version,
        [(r'(^version\s*=\s*)"[^"]*"', "version field")],
        "pyproject.toml",
    )

    replace_versions(
        PACKAGE_JSON,
        version,
        [(r'(^  "version"\s*:\s*)"[^"]*"', "top-level version field")],
        "package.json",
    )

    replace_versions(
        PACKAGE_LOCK,
        version,
        [
            (r'(^  "version"\s*:\s*)"[^"]*"', "top-level version field"),
            (r'(""\s*:\s*\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"version"\s*:\s*)"[^"]*"', "root package version field"),
        ],
        "package-lock.json",
    )


if __name__ == "__main__":
    sync()
