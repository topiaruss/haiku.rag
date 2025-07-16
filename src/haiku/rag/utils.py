import sys
from importlib import metadata
from pathlib import Path

import httpx
from packaging.version import Version, parse


def get_default_data_dir() -> Path:
    """Get the user data directory for the current system platform.

    Linux: ~/.local/share/haiku.rag
    macOS: ~/Library/Application Support/haiku.rag
    Windows: C:/Users/<USER>/AppData/Roaming/haiku.rag

    Returns:
        User Data Path.
    """
    home = Path.home()

    system_paths = {
        "win32": home / "AppData/Roaming/haiku.rag",
        "linux": home / ".local/share/haiku.rag",
        "darwin": home / "Library/Application Support/haiku.rag",
    }

    data_path = system_paths[sys.platform]
    return data_path


def semantic_version_to_int(version: str) -> int:
    """Convert a semantic version string to an integer.

    Args:
        version: Semantic version string.

    Returns:
        Integer representation of semantic version.
    """
    major, minor, patch = version.split(".")
    major = int(major) << 16
    minor = int(minor) << 8
    patch = int(patch)
    return major + minor + patch


def int_to_semantic_version(version: int) -> str:
    """Convert an integer to a semantic version string.

    Args:
        version: Integer representation of semantic version.

    Returns:
        Semantic version string.
    """
    major = version >> 16
    minor = (version >> 8) & 255
    patch = version & 255
    return f"{major}.{minor}.{patch}"


async def is_up_to_date() -> tuple[bool, Version, Version]:
    """Check whether haiku.rag is current.

    Returns:
        A tuple containing a boolean indicating whether haiku.rag is current,
        the running version and the latest version.
    """

    async with httpx.AsyncClient() as client:
        running_version = parse(metadata.version("haiku.rag"))
        try:
            response = await client.get("https://pypi.org/pypi/haiku.rag/json")
            data = response.json()
            pypi_version = parse(data["info"]["version"])
        except Exception:
            # If no network connection, do not raise alarms.
            pypi_version = running_version
    return running_version >= pypi_version, running_version, pypi_version
