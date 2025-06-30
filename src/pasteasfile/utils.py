# utils.py

import sys
import pathlib

def get_asset_path(filename: str) -> str:
    """
    Gets the absolute path to an asset file.

    This function correctly resolves paths for both normal execution
    and for a PyInstaller "frozen" executable.
    """
    if getattr(sys, "frozen", False):
        # When frozen by PyInstaller, assets are bundled in the temp directory.
        # We configure pyinstaller to place them in the root of that temp dir.
        base_path = pathlib.Path(sys._MEIPASS)
    else:
        # In development, assets are in the 'assets' directory at the project root.
        # This path is relative to this file's location.
        base_path = pathlib.Path(__file__).resolve().parents[2] / "assets"

    return str(base_path / filename)