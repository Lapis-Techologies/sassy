from importlib import import_module
from io import StringIO
from pathlib import Path
from collections import namedtuple
from argparse import ArgumentParser


Version = namedtuple("Version", ["MAJOR", "MINOR", "PATCH"])


def update_markdown(version: str) -> None:
    """Update the version badge in README.md."""
    with open("README.md", "r") as readme:
        lines = readme.readlines()

    new_line = f'    <img alt="Version" src="https://img.shields.io/badge/Version-{version}-green">\n'
    for i, line in enumerate(lines):
        if '<img alt="Version' in line:
            lines[i] = new_line
            with open("README.md", "w") as readme:
                readme.writelines(lines)
            return
    print("[-] Couldn't find version tag inside readme file!")


def load_version() -> Version:
    """Load the version file or create a default if it doesn't exist."""
    try:
        module = import_module("version")
        return variable_check(module)
    except ImportError as e:
        if Path("version.py").exists():
            raise ValueError("version.py is malformed!") from e
        else:
            with open("version.py", "w") as file:
                file.write("MAJOR = 0\nMINOR = 0\nPATCH = 0\n")
            return Version(0, 0, 0)


def variable_check(version) -> Version:
    """Check if required version variables exist in the module."""
    return Version(
        getattr(version, "MAJOR", 0),
        getattr(version, "MINOR", 0),
        getattr(version, "PATCH", 0),
    )


def update_version(changes: tuple[int, int, int], version: Version) -> Version:
    """
    Update version based on changes (increment/decrement for major, minor, patch).
    Returns new Version tuple, ensuring non-negative values.
    """
    major_change, minor_change, patch_change = changes
    new_major, new_minor, new_patch = version.MAJOR, version.MINOR, version.PATCH

    if major_change != 0:
        new_major += major_change
        new_minor, new_patch = 0, 0
    elif minor_change != 0:
        new_minor += minor_change
        new_patch = 0
    elif patch_change != 0:
        new_patch += patch_change

    # Validate non-negative version numbers
    if new_major < 0 or new_minor < 0 or new_patch < 0:
        raise ValueError("Version numbers cannot be negative!")

    return Version(new_major, new_minor, new_patch)


def write(version: Version) -> None:
    """Write version numbers to version.py."""
    script = StringIO()
    script.write(f"# THIS FILE WAS AUTOMATICALLY GENERATED BY {__file__}\n")
    script.write(f"# DO NOT EDIT THIS FILE MANUALLY! USE {__file__}\n\n")
    script.write(f"MAJOR = {version.MAJOR}\n")
    script.write(f"MINOR = {version.MINOR}\n")
    script.write(f"PATCH = {version.PATCH}\n")

    with open("version.py", "w") as file:
        script.seek(0)
        file.write(script.read())


def main() -> None:
    parser = ArgumentParser(description="Manage Sassy Bot version numbers")
    parser.add_argument(
        "-M", "--major", action="store_true", help="Increment major version"
    )
    parser.add_argument(
        "-m", "--minor", action="store_true", help="Increment minor version"
    )
    parser.add_argument(
        "-p", "--patch", action="store_true", help="Increment patch version"
    )
    parser.add_argument(
        "-dM", "--decrement-major", action="store_true", help="Decrement major version"
    )
    parser.add_argument(
        "-dm", "--decrement-minor", action="store_true", help="Decrement minor version"
    )
    parser.add_argument(
        "-dp", "--decrement-patch", action="store_true", help="Decrement patch version"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Print current version and exit"
    )

    args = parser.parse_args()

    # Load current version
    version = load_version()

    # Handle quiet mode
    if args.quiet and not any(
        [
            args.major,
            args.minor,
            args.patch,
            args.decrement_major,
            args.decrement_minor,
            args.decrement_patch,
        ]
    ):
        print(f"{version.MAJOR}.{version.MINOR}.{version.PATCH}")
        return

    # Validate that only one type of update is specified
    updates = [
        (args.major, "major increment"),
        (args.decrement_major, "major decrement"),
        (args.minor, "minor increment"),
        (args.decrement_minor, "minor decrement"),
        (args.patch, "patch increment"),
        (args.decrement_patch, "patch decrement"),
    ]
    active_updates = [update for update, _ in updates if update]
    if len(active_updates) > 1:
        raise ValueError(
            "Only one version update (increment or decrement) can be specified at a time."
        )
    elif len(active_updates) == 0:
        print(f"Sassy Bot Version {version.MAJOR}.{version.MINOR}.{version.PATCH}")
        return

    # Determine changes
    changes = (
        1 if args.major else -1 if args.decrement_major else 0,
        1 if args.minor else -1 if args.decrement_minor else 0,
        1 if args.patch else -1 if args.decrement_patch else 0,
    )

    # Update version
    try:
        new_version = update_version(changes, version)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Write new version and update README
    write(new_version)
    update_markdown(f"{new_version.MAJOR}.{new_version.MINOR}.{new_version.PATCH}")

    # Print results
    action = next(label for update, label in updates if update)
    print(
        f"Sassy Bot Version {new_version.MAJOR}.{new_version.MINOR}.{new_version.PATCH}"
    )
    print(f"Performed {action}.")


if __name__ == "__main__":
    main()
