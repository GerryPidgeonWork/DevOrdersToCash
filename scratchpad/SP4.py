# ====================================================================================================
# SP4.py
# ----------------------------------------------------------------------------------------------------
# Scratchpad script for ad-hoc testing, experiments, and quick validation.
#
# IMPORTANT:
#   - This file is NOT production code.
#   - This file is NOT part of the Core or GUI libraries.
#   - This file may be freely modified, reset, or deleted.
#
# Intended Use:
#   - Temporary experiments
#   - Manual tests
#   - One-off checks during development
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
from __future__ import annotations

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys
from pathlib import Path

# --- Ensure project root DOES NOT override site-packages ---------------------------------------------
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

# --- Initialise module-level logger ------------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging, DEBUG
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# (Scratchpad-only imports are allowed here, but must still respect C00 rules)


# ====================================================================================================
# 3. SCRATCHPAD IMPLEMENTATION
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Temporary logic for experimentation and testing.
#
# Rules:
#   - No assumptions of stability or reuse.
#   - Code here may be deleted or rewritten at any time.
#   - DO NOT promote logic from this section directly into Core or GUI modules.
#   - If functionality proves reusable, extract it into the appropriate governed module.
# ====================================================================================================


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
# Rules:
#   - No side-effects at import time.
#   - Initialisation (e.g., logging) must be triggered here.
#   - Any test or demonstration logic should be gated behind __main__.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Entry point for scratchpad testing.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - This is NOT a production entry point.
        - Keep logic simple and disposable.
    """
    logger.info("SP1 scratchpad started.")

    logger.info("SP1 scratchpad finished.")


if __name__ == "__main__":
    init_logging()
    main()
