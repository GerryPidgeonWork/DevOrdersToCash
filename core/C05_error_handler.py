# ====================================================================================================
# C05_error_handler.py
# ----------------------------------------------------------------------------------------------------
# Centralised error handling for all PyBaseEnv projects.
#
# Purpose:
#   - Provide a unified error-handling interface for CLI and service-style applications.
#   - Capture and log all uncaught exceptions via sys.excepthook.
#   - Support manual error capture with contextual logging.
#   - Honour configuration flags for fatal-exit behaviour.
#
# Usage:
#   from core.C05_error_handler import (
#       install_global_exception_hook,
#       handle_error,
#   )
#
#   install_global_exception_hook()
#
#   try:
#       risky_operation()
#   except Exception as e:
#       handle_error(e, context="During import process")
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
from core.C04_config_loader import get_config


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

# --- Global Error Handling Functions -----------------------------------------------------------------
def handle_error(exception: Exception, context: str = "", fatal: bool = False) -> None:
    """
    Description:
        Handles an exception by logging it and optionally triggering a fatal exit
        depending on configuration settings.

    Args:
        exception (Exception): The exception object to be handled.
        context (str, optional): Additional information describing where the error
            occurred. Defaults to an empty string.
        fatal (bool, optional): Whether the error should be treated as fatal. If True,
            behaviour depends on CONFIG["error_handling"]["exit_on_fatal"]. Defaults to False.

    Returns:
        None.

    Raises:
        SystemExit: If fatal=True and configuration enables fatal exiting.

    Notes:
        - All exceptions are logged with full traceback via log_exception().
        - Safe for use in CLI tools, services, and background workers.
    """
    log_exception(exception, context=context)

    exit_on_fatal = get_config("error_handling", "exit_on_fatal", default=False)
    if fatal and exit_on_fatal:
        logger.error("💀 Fatal error encountered. Exiting application.")
        sys.exit(1)


def global_exception_hook(exc_type, exc_value, exc_traceback) -> None:
    """
    Description:
        Global fallback handler for uncaught exceptions. Installed via
        install_global_exception_hook().

    Args:
        exc_type (type): The exception class.
        exc_value (Exception): The exception instance.
        exc_traceback (TracebackType): The associated traceback.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - KeyboardInterrupt is passed through cleanly to avoid noisy logs.
        - All other exceptions are logged and routed to handle_error() with fatal=True.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("🛑 Application interrupted by user (Ctrl+C).")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("❌ Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    handle_error(exc_value, context="Unhandled Exception", fatal=True)


def install_global_exception_hook() -> None:
    """
    Description:
        Installs the custom global exception hook to ensure all uncaught exceptions
        are processed by this module's logic.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Replaces sys.excepthook.
        - Future uncaught exceptions will be logged and handled consistently.
    """
    sys.excepthook = global_exception_hook
    logger.info("🛡️ Global exception hook installed.")


# --- Manual Test Function ----------------------------------------------------------------------------
def simulate_error() -> None:
    """
    Description:
        Raises a controlled ValueError for manual testing of error handlers.

    Args:
        None.

    Returns:
        None.

    Raises:
        ValueError: Always raised to simulate an error condition.

    Notes:
        - Used only for standalone testing.
    """
    raise ValueError("This is a simulated test exception.")


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
    "handle_error",
    "global_exception_hook",
    "install_global_exception_hook",
    "simulate_error",
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
        Self-test entry point for C05_error_handler.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates error handling and global exception hook.
    """
    logger.info("C05_error_handler self-test started.")
    install_global_exception_hook()

    try:
        simulate_error()
    except Exception as error:
        handle_error(error, context="During standalone test")

    logger.info("Testing fatal error behaviour (if enabled in config)...")

    try:
        handle_error(
            Exception("This is a simulated fatal error."),
            context="Fatal test",
            fatal=True,
        )
    except SystemExit:
        logger.info("💥 Fatal exit triggered successfully (SystemExit caught for test).")

    logger.info("C05_error_handler self-test completed successfully.")


if __name__ == "__main__":
    init_logging()
    main()