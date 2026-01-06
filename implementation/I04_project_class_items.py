# ====================================================================================================
# I04_project_class_items.py
# ----------------------------------------------------------------------------------------------------
# Central repository for project-specific class definitions and data structures.
#
# Purpose:
#   - Define shared dataclasses, named tuples, and custom types.
#   - Provide type-safe containers for passing data between modules.
#   - Keep class definitions separate from business logic for maintainability.
#
# Typical Contents (to be added as needed):
#   - Dataclasses for structured data (e.g., ReconciliationResult, ProviderConfig)
#   - Named tuples for immutable records
#   - Enums for fixed value sets
#   - TypedDicts for dictionary type hints
#
# Usage:
#   from implementation.I04_project_class_items import ReconciliationResult
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-10
# Project:      Orders-to-Cash v1.0
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
# (No additional imports required - dataclass decorator available via C00)


# ====================================================================================================
# 3. CLASS DEFINITIONS
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define dataclasses, named tuples, and custom types for the Orders-to-Cash project.
#   Add new class definitions below as needed.
#
# Guidelines:
#   - Use @dataclass for mutable structured data
#   - Use NamedTuple for immutable records
#   - Use Enum for fixed value sets
#   - Include docstrings with field descriptions
# ====================================================================================================

# (Add class definitions here as needed)


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
__all__ = [
    # (Add exported class names here as they are defined)
]


# ====================================================================================================
# 99. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
def main() -> None:
    """
    Description:
        Self-test for I04_project_class_items module.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Validates that all exported classes are importable.
        - Add specific class tests as classes are defined.
    """
    logger.info("📦 I04_project_class_items self-test started.")

    # ------------------------------------------------------------------
    # VALIDATE EXPORTS
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Validating exported classes...")
    logger.info("-" * 60)

    if not __all__:
        logger.info("  (No classes defined yet)")
    else:
        for name in __all__:
            obj = globals().get(name)
            if obj is not None:
                logger.info("  ✓ %s: %s", name.ljust(30), type(obj).__name__)
            else:
                logger.warning("  ✗ %s: NOT FOUND", name)

    logger.info("-" * 60)
    logger.info("✅ I04_project_class_items self-test complete.")


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()
