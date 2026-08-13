import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "src" / "version.py"
PYPROJECT = ROOT / "pyproject.toml"


def load_app_version() -> str:
    match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', VERSION_FILE.read_text())
    if not match:
        sys.exit("APP_VERSION not found in src/version.py")
    return match.group(1)


def sync() -> None:
    version = load_app_version()
    text = PYPROJECT.read_text()
    new_text, n = re.subn(r'(^version\s*=\s*)"[^"]*"', rf'\g<1>"{version}"', text, count=1, flags=re.M)
    if n == 0:
        sys.exit("version field not found in pyproject.toml")
    if new_text != text:
        PYPROJECT.write_text(new_text)
        print(f"synced pyproject.toml version -> {version}")
    else:
        print("pyproject.toml already in sync")


if __name__ == "__main__":
    sync()
