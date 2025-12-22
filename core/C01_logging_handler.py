# ====================================================================================================
# C01_logging_handler.py
# ----------------------------------------------------------------------------------------------------
# Centralised logging controller for all modules using CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Provide a safe, explicit entry point for logging configuration.
#   - Standardise log formats and handlers (file + optional console).
#   - Offer optional print() redirection into the logging system.
#   - Expose helper utilities: get_logger, log_divider, log_exception.
#   - Re-export logging level constants for consistent imports across the codebase.
#
# Usage:
#   from core.C01_logging_handler import (
#       init_logging,
#       get_logger,
#       log_exception,
#       DEBUG,
#   )
#
#   init_logging()
#   logger = get_logger(__name__)
#   logger.info("Logging initialised")
#
# Architectural Notes:
#   - This module cannot import core.C01_set_file_paths because C01 depends on C03.
#     To avoid circular dependencies, LOGS_DIR is derived directly from project_root.
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
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_logging_handler is a pure core module and must not import GUI packages.
#
# NOTE:
#   This module DEFINES the logging helpers (get_logger, init_logging, etc.), so it
#   cannot import them from itself. Instead, it uses the logging package provided via
#   core.C00_set_packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Base module-level logger -----------------------------------------------------------------------
# Direct use of logging.getLogger is permitted ONLY in this module, because it
# bootstraps the logging system for all other modules.
logger: logging.Logger = logging.getLogger(__name__)

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

# --- Logging Level Re-exports ------------------------------------------------------------------------
# Re-export logging level constants so all modules can import everything logging-related from C01.
# This ensures C01 is the single source of truth for all logging needs.
DEBUG: int = logging.DEBUG
INFO: int = logging.INFO
WARNING: int = logging.WARNING
ERROR: int = logging.ERROR
CRITICAL: int = logging.CRITICAL


# --- Logging Constants & State -----------------------------------------------------------------------
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# LOGS_DIR cannot come from C01 to avoid circular dependency.
LOGS_DIR: Path = Path(project_root) / "logs"

logging_configured: bool = False
active_log_file: Path | None = None
original_stdout: Any = sys.stdout


# --- Logging Initialisation --------------------------------------------------------------------------
def init_logging(
    log_directory: Path | None = None,
    level: int = logging.INFO,
    enable_console: bool = True,
) -> None:
    """
    Description:
        Initialises application-wide logging in an idempotent manner.

    Args:
        log_directory (Path | None): Directory where log files will be stored.
            If None, LOGS_DIR is used.
        level (int): Base logging level for the root logger.
        enable_console (bool): Whether a console handler (stdout) is attached.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Safe to call multiple times. Only the first call performs configuration.
        - Delegates to configure_logging() for actual configuration.
    """
    global logging_configured

    if logging_configured:
        return

    configure_logging(log_directory=log_directory, level=level, enable_console=enable_console)


def configure_logging(
    log_directory: Path | None = None,
    level: int = logging.INFO,
    enable_console: bool = True,
) -> Path | None:
    """
    Description:
        Configures the root logging system with file and optional console handlers.

    Args:
        log_directory (Path | None): Directory in which the log file will be created.
        level (int): Base logging level applied to the root logger.
        enable_console (bool): Whether to attach a console StreamHandler.

    Returns:
        Path | None: The path to the active log file, or None if already configured.

    Raises:
        OSError: If log directory creation or file access fails.

    Notes:
        - LOGS_DIR is used by default to avoid circular dependencies.
        - Adds handlers only once even if called multiple times.
        - Ensures a daily rotating log file based on date.
    """
    global logging_configured, active_log_file

    if logging_configured:
        return active_log_file

    log_directory = log_directory or LOGS_DIR
    log_directory.mkdir(parents=True, exist_ok=True)

    active_log_file = log_directory / f"{dt.datetime.now():%Y-%m-%d}.log"

    file_handler = logging.FileHandler(active_log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    handlers: list[logging.Handler] = [file_handler]

    if enable_console:
        console_handler = logging.StreamHandler(original_stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        handlers.append(console_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in handlers:
        root_logger.addHandler(handler)

    logging_configured = True
    logger.debug("Logging configured. Log file: %s", active_log_file)
    return active_log_file


# --- Print Redirection -------------------------------------------------------------------------------
class PrintRedirector(io.StringIO):
    """
    Description:
        Redirects print() output to the logging system while preserving standard output.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Used by enable_print_redirection() and disable_print_redirection().
        - Non-empty messages are logged at INFO level.
    """

    def write(self, msg: str) -> int:
        """
        Description:
            Writes a message to both the logging system and original stdout.

        Args:
            msg (str): The message text to output.

        Returns:
            int: Number of characters written to the original stdout.

        Raises:
            None.

        Notes:
            - Called whenever print() is invoked while redirection is active.
        """
        if msg.strip():
            logging.info(msg.strip())
        return original_stdout.write(msg)

    def flush(self) -> None:
        """
        Description:
            Flushes the underlying original stdout stream.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Ensures stdout remains flushable when redirection is active.
        """
        original_stdout.flush()


def enable_print_redirection() -> None:
    """
    Description:
        Redirects all future print() calls to the logging system.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Replaces sys.stdout with a PrintRedirector instance.
    """
    sys.stdout = PrintRedirector()


def disable_print_redirection() -> None:
    """
    Description:
        Restores standard print() behaviour by resetting stdout.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Reverses enable_print_redirection().
    """
    sys.stdout = original_stdout


# --- Logger Utilities --------------------------------------------------------------------------------
def get_logger(name: str | None = None) -> logging.Logger:
    """
    Description:
        Returns a logger instance with the given name.

    Args:
        name (str | None): The logger name, or None for the root logger.

    Returns:
        logging.Logger: The corresponding logger instance.

    Raises:
        None.

    Notes:
        - Wrapper around logging.getLogger().
    """
    return logging.getLogger(name)


def log_divider(level: str = "info", label: str = "", width: int = 80) -> None:
    """
    Description:
        Writes a divider line to the log at the specified level.

    Args:
        level (str): Logging level name (e.g., "info").
        label (str): Optional label to insert into the divider.
        width (int): Width of the divider line.

    Returns:
        None.

    Raises:
        AttributeError: If the logging level name is invalid.

    Notes:
        - Useful for separating logical sections in logs.
    """
    text = f" {label} " if label else ""
    line = text.center(width, "-")
    divider_logger = get_logger("divider")
    divider_logger.log(getattr(logging, level.upper()), line)


def log_exception(
    exception: Exception,
    logger_instance: logging.Logger | None = None,
    context: str = "",
) -> None:
    """
    Description:
        Logs an exception including its full traceback.

    Args:
        exception (Exception): The exception instance.
        logger_instance (logging.Logger | None): Logger to use. If None, an
            'exception' logger is used.
        context (str): Optional contextual label for where the exception occurred.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Ensures consistent formatting and traceback capture.
    """
    active_logger = logger_instance or get_logger("exception")
    context_text = f" during {context}" if context else ""
    msg = f"Exception occurred{context_text}: {exception}"
    active_logger.error(msg, exc_info=True)


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
    # --- Logging Level Constants (re-exported from logging) ---
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    # --- Module Constants ---
    "LOG_FORMAT",
    "DATE_FORMAT",
    "LOGS_DIR",
    "active_log_file",
    # --- Initialisation ---
    "init_logging",
    "configure_logging",
    # --- Print Redirection ---
    "PrintRedirector",
    "enable_print_redirection",
    "disable_print_redirection",
    # --- Logger Utilities ---
    "get_logger",
    "log_divider",
    "log_exception",
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
        Self-test entry point for C01_logging_handler.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates logging initialisation, divider output, and exception logging.
        - Validates logging level re-exports.
    """
    logger.info("C01_logging_handler self-test started.")
    log_divider(label="C01 Logging Handler Verification")

    # Validate logging level re-exports
    assert DEBUG == 10, f"DEBUG should be 10, got {DEBUG}"
    assert INFO == 20, f"INFO should be 20, got {INFO}"
    assert WARNING == 30, f"WARNING should be 30, got {WARNING}"
    assert ERROR == 40, f"ERROR should be 40, got {ERROR}"
    assert CRITICAL == 50, f"CRITICAL should be 50, got {CRITICAL}"
    logger.info("Logging level re-exports validated: DEBUG=%s, INFO=%s, WARNING=%s, ERROR=%s, CRITICAL=%s",
                DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Test isEnabledFor pattern
    if logger.isEnabledFor(DEBUG):
        logger.debug("Debug logging is enabled")
    else:
        logger.info("Debug logging is disabled (level is INFO or higher)")

    try:
        test_value = 1 / 0  # Intentional error for testing
        logger.debug("Test value (should not be reached): %s", test_value)
    except Exception as exc:
        log_exception(exc, context="Sample division test in self-test")

    logger.info("C01_logging_handler self-test completed successfully.")


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()