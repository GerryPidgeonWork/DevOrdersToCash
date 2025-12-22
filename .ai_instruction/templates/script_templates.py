# ====================================================================================================
# TEMPLATE INSTRUCTIONS — DELETE THIS BLOCK AFTER USE
# ====================================================================================================
# 1. Replace all {{PLACEHOLDER}} values with actual values
# 2. Add imports below the designated line in Section 2
# 3. Implement classes/functions starting in Section 3
#    - For simple scripts, Section 3 alone may be sufficient
#    - For complex modules, add Sections 4, 5, 6, ... as needed
# 4. Expose public API in Section 98 if needed
# 5. Add test logic in Section 99 main() if needed
# 6. Delete this instruction block entirely
# ====================================================================================================


# ====================================================================================================
# {{SCRIPT_NAME}}.py
# ----------------------------------------------------------------------------------------------------
# {{SCRIPT_DESCRIPTION}}
#
# ----------------------------------------------------------------------------------------------------
# Author:       {{AUTHOR}}
# Created:      {{DATE}}
# Project:      {{PROJECT_NAME}}
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
from core.C01_logging_handler import get_logger, log_exception, init_logging, DEBUG
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# {{ADDITIONAL_IMPORTS}}


# ====================================================================================================
# 3. MODULE IMPLEMENTATION
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Implementation sections begin here. For simple scripts, Section 3 may be sufficient.
#   For complex modules, use additional numbered sections (4, 5, 6, ...) to organise
#   logically distinct groupings (e.g., constants, cache, helpers, core engine, convenience
#   functions, introspection utilities).
#
# Section Layout:
#   - Sections 1 and 2 are LOCKED (system/project imports).
#   - Sections 3 through 97 are FLEXIBLE for implementation.
#   - Section 98 is LOCKED (public API surface).
#   - Section 99 is LOCKED (main execution / self-test).
#
# Rules:
#   - No execution or side-effects in implementation sections.
#   - Each section should have a clear, single responsibility.
#   - Use descriptive section titles (e.g., "4. INTERNAL HELPERS", "5. CORE ENGINE").
# ====================================================================================================

# {{IMPLEMENTATION}}


# ====================================================================================================
# 98. PUBLIC API SURFACE (OPTIONAL)
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
# ====================================================================================================

# __all__ = [{{PUBLIC_API}}]


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
        Optional entry point for development testing or demonstration runs.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Keep this lightweight.
        - Use logger for all output.
    """
    logger.info("{{SCRIPT_NAME}} self-test initialised.")
    # {{SELF_TEST}}


if __name__ == "__main__":
    init_logging()
    main()