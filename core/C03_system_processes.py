# ====================================================================================================
# C03_system_processes.py
# ----------------------------------------------------------------------------------------------------
# Provides environment detection and user folder resolution utilities.
#
# Purpose:
#   - Detect the user's operating environment (Windows, macOS, WSL, Linux, or iOS).
#   - Dynamically determine the correct default Downloads folder for file operations.
#   - Support cross-platform compatibility for all projects using PyBaseEnv.
#
# Usage:
#   from core.C03_system_processes import detect_os, user_download_folder
#
# Example:
#   >>> detect_os()
#   'Windows (WSL)'
#   >>> user_download_folder()
#   WindowsPath('C:/Users/username/Downloads')
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2026-01-01
# Project:      PyBaseEnv
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# (None required for this module)


# ====================================================================================================
# 3. MODULE IMPLEMENTATION (CLASSES / FUNCTIONS)
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define implementation elements that are internal to this module, such as helper functions and
#   classes. These items are not intended for external reuse unless explicitly promoted to the
#   public API (Section 98).
#
# Rules:
#   - Items here are local to this script and support its specific purpose.
#   - Do not implement reusable utilities here; move those into shared implementation modules.
#   - Do not implement cross-project abstractions here; elevate those to Core modules.
#   - No execution or side-effects in this section.
# ====================================================================================================

# --- Operating System Detection ----------------------------------------------------------------------
def detect_os() -> str:
    """
    Description:
        Detects the current operating system or runtime environment and returns a
        descriptive string label.

    Args:
        None.

    Returns:
        str: A human-readable label describing the detected OS (e.g. "Windows",
             "Windows (WSL)", "macOS", "Linux", "iOS").

    Raises:
        None.

    Notes:
        - Detection uses sys.platform, platform.uname(), and machine architecture.
        - iOS detection relies on macOS runtime signatures such as iPhone/iPad identifiers.
        - Logging is used for debug-level tracing of decisions.
    """
    if sys.platform == "win32":
        result = "Windows"

    elif sys.platform == "darwin":
        machine = platform.machine() or ""
        if machine.startswith(("iP",)):  # iPhone / iPad
            result = "iOS"
        else:
            result = "macOS"

    elif sys.platform.startswith("linux"):
        release = platform.uname().release.lower()
        if "microsoft" in release or "wsl" in release:
            result = "Windows (WSL)"
        else:
            result = "Linux"

    else:
        result = sys.platform

    logger.debug("OS detected: %s", result)
    return result


# --- User Download Folder Detection ------------------------------------------------------------------
def user_download_folder() -> Path:
    """
    Description:
        Determines the appropriate user "Downloads" folder for the current operating
        system environment.

    Args:
        None.

    Returns:
        Path: The resolved path to the user's expected Downloads directory.

    Raises:
        None.

    Notes:
        - Supports Windows, WSL, macOS, Linux, and iOS.
        - Never creates directories; only performs detection.
        - Under WSL, attempts to resolve the Windows-side Downloads folder when possible.
        - Falls back cleanly if access or resolution fails.
    """
    os_type = detect_os()
    home = Path.home()

    if os_type == "Windows":
        result = home / "Downloads"

    elif os_type == "Windows (WSL)":
        try:
            linux_user = getpass.getuser()
            win_path_guess = Path(f"/mnt/c/Users/{linux_user}/Downloads")

            if win_path_guess.exists():
                result = win_path_guess
            else:
                result = home / "Downloads"

        except Exception:
            result = home / "Downloads"

    elif os_type == "macOS":
        result = home / "Downloads"

    elif os_type == "Linux":
        result = home / "Downloads"

    elif os_type == "iOS":
        result = home  # iOS sandboxes have no Downloads folder

    else:
        result = home

    logger.debug("Resolved user download folder: %s", result)
    return result


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Declare a concise, intentional list of functions or objects that this module exposes for external
#   use. This section acts as a "public interface" and prevents accidental consumption of internal
#   helpers or implementation details.
#
# Rules:
#   - Only list functions or objects that are explicitly intended to be imported by other modules.
#   - Do NOT expose one-off helpers or short-lived utilities; those must remain internal to this file.
#   - If more than a small number of items belong here, consider whether they should be elevated to a
#     shared implementation module or to the Core library (C-modules).
#   - This section must contain no executable code and no import statements.
#   - For Python enforcement, "__all__" may be declared here, but this is optional.
#
# Benefit:
#   This provides a predictable "contract location" across the codebase, improving navigability,
#   reducing implicit coupling, and discouraging scripts from evolving into accidental libraries.
# ----------------------------------------------------------------------------------------------------

__all__ = [
    "detect_os",
    "user_download_folder",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
# Rules:
#   - No side-effects at import time.
#   - Initialisation (e.g., logging) must be triggered here.
#   - Any test or demonstration logic should be gated behind __main__.
#
# This ensures safe importing from other modules and prevents hidden execution paths.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Self-test entry point for C03_system_processes.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates OS detection and download folder resolution.
    """
    logger.info("C03_system_processes self-test started.")
    logger.info("Detected OS    : %s", detect_os())
    logger.info("Download folder: %s", user_download_folder())
    logger.info("C03_system_processes self-test completed successfully.")


if __name__ == "__main__":
    init_logging()
    main()