# ====================================================================================================
# C15_cache_manager.py
# ----------------------------------------------------------------------------------------------------
# Provides a lightweight caching framework for temporary or reusable data.
#
# Purpose:
#   - Store and retrieve frequently used data (e.g., API responses, DataFrames, query results).
#   - Improve performance by avoiding repeated expensive operations.
#   - Ensure consistent cache directory handling across all projects.
#
# Supported Formats:
#   - JSON for dictionary-like data.
#   - CSV for Pandas DataFrames.
#   - Pickle for arbitrary Python objects.
#
# Usage:
#   from core.C15_cache_manager import (
#       save_cache,
#       load_cache,
#       clear_cache,
#       list_cache_files,
#       get_cache_path,
#   )
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
from core.C02_set_file_paths import PROJECT_ROOT
from core.C07_datetime_utils import as_str, get_today
from core.C06_validation_utils import validate_directory_exists


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

# --- Global Settings ---------------------------------------------------------------------------------
# NOTE:
#   - CACHE_DIR is defined as a Path but the directory is NOT created at import time.
#   - Use ensure_cache_dir() to create/validate the cache directory when needed.
CACHE_DIR: Path = PROJECT_ROOT / "cache"


def ensure_cache_dir() -> Path:
    """
    Description:
        Ensure that the cache directory exists and return its path.

    Args:
        None.

    Returns:
        Path:
            The validated cache directory path as a Path instance.

    Raises:
        FileNotFoundError:
            Propagated from validate_directory_exists() if directory creation fails
            and the underlying function raises.

    Notes:
        This function may be called multiple times safely; the underlying directory
        creation uses exist_ok=True semantics via validate_directory_exists().
    """
    validate_directory_exists(CACHE_DIR, create_if_missing=True)
    return CACHE_DIR


# --- Core Cache Functions ----------------------------------------------------------------------------
def get_cache_path(name: str, fmt: str = "json") -> Path:
    """
    Description:
        Build the full path to a cache file in the cache directory.

    Args:
        name (str):
            Logical name for the cache file (for example, "orders_today").
        fmt (str, optional):
            File format for the cache. Supported options are:
                - "json": JSON object.
                - "csv":  Pandas DataFrame.
                - "pkl":  Pickled Python object.
            Defaults to "json".

    Returns:
        Path:
            Fully resolved filesystem path of the cache file in CACHE_DIR.

    Raises:
        None.

    Notes:
        If an unrecognised format is supplied, the extension defaults to ".json"
        but no validation is performed here. Validation is enforced in save_cache()
        and load_cache().
    """
    base_dir = ensure_cache_dir()
    extension_map = {"json": ".json", "csv": ".csv", "pkl": ".pkl"}
    ext = extension_map.get(fmt.lower(), ".json")
    return base_dir / f"{name}{ext}"


def save_cache(name: str, data: Any, fmt: str = "json") -> Path | None:
    """
    Description:
        Save data to a cache file in the specified format.

    Args:
        name (str):
            Name of the cache file without extension.
        data (Any):
            The data or object to be cached. For CSV format, this must be a
            pandas DataFrame instance.
        fmt (str, optional):
            Cache format, one of:
                - "json"
                - "csv"
                - "pkl"
            Defaults to "json".

    Returns:
        Path | None:
            The Path where the cache was saved on success; otherwise None if an
            error occurs during serialisation or I/O.

    Raises:
        ValueError:
            If an unsupported cache format is requested or if CSV format is used
            with a non-DataFrame object.

    Notes:
        - All unexpected exceptions are logged via log_exception() and result in
          a None return value.
        - JSON caches are written with UTF-8 encoding and indent=2.
    """
    fmt = fmt.lower()
    if fmt not in {"json", "csv", "pkl"}:
        raise ValueError(f"Unsupported cache format '{fmt}'. Use 'json', 'csv', or 'pkl'.")

    path = get_cache_path(name, fmt)

    try:
        if fmt == "json":
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        elif fmt == "csv":
            if not isinstance(data, pd.DataFrame):
                raise ValueError("CSV cache format requires a pandas DataFrame.")
            data.to_csv(path, index=False)
        else:  # "pkl"
            with open(path, "wb") as file:
                pickle.dump(data, file)

        logger.info("💾 Cache saved: %s", path.name)
        return path

    except Exception as error:
        log_exception(error, context=f"saving cache '{name}' ({fmt})")
        return None


def load_cache(name: str, fmt: str = "json") -> Any:
    """
    Description:
        Load cached data from disk if it exists.

    Args:
        name (str):
            Name of the cache file without extension.
        fmt (str, optional):
            Cache file format. Supported values:
                - "json"
                - "csv"
                - "pkl"
            Defaults to "json".

    Returns:
        Any:
            The loaded cached data (for example, dict, DataFrame, or arbitrary
            Python object), or None if the cache file does not exist or an
            unexpected error occurs.

    Raises:
        ValueError:
            If an unsupported cache format is requested.

    Notes:
        - Missing cache files are treated as a non-error condition; the function
          logs a warning and returns None.
        - Unexpected exceptions are logged via log_exception() and result in
          a None return value.
    """
    fmt = fmt.lower()
    if fmt not in {"json", "csv", "pkl"}:
        raise ValueError(f"Unsupported cache format '{fmt}'. Use 'json', 'csv', or 'pkl'.")

    path = get_cache_path(name, fmt)

    if not path.exists():
        logger.warning("⚠️  Cache not found: %s", path.name)
        return None

    try:
        if fmt == "json":
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        elif fmt == "csv":
            data = pd.read_csv(path)
        else:
            with open(path, "rb") as file:
                data = pickle.load(file)

        logger.info("✅ Cache loaded: %s", path.name)
        return data

    except Exception as error:
        log_exception(error, context=f"loading cache '{name}' ({fmt})")
        return None


def clear_cache(name: str | None = None) -> None:
    """
    Description:
        Delete one specific cache or clear all cache files.

    Args:
        name (str | None):
            Identifier of a specific cache to remove. If None, all cache files
            in CACHE_DIR are deleted.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Any file-system errors encountered during deletion are logged via
          log_exception() and do not stop processing of other files.
        - If a specific named cache is not found, a warning is logged.
    """
    base_dir = ensure_cache_dir()

    if name:
        deleted = False
        for fmt in ("json", "csv", "pkl"):
            path = get_cache_path(name, fmt)
            if path.exists():
                try:
                    path.unlink()
                    logger.info("🗑️  Deleted cache: %s", path.name)
                    deleted = True
                except Exception as error:
                    log_exception(error, context=f"deleting cache file '{path}'")
        if not deleted:
            logger.warning("⚠️  No cache found for '%s'.", name)
    else:
        files = list(base_dir.glob("*"))
        for file_path in files:
            try:
                file_path.unlink()
            except Exception as error:
                log_exception(error, context=f"clearing cache file '{file_path}'")
        logger.info("🧹 Cleared %d cache file(s) from %s.", len(files), base_dir)


def list_cache_files() -> list[Path]:
    """
    Description:
        List all cache files currently present in the cache directory.

    Args:
        None.

    Returns:
        list[Path]:
            List of Path objects representing cache files found in CACHE_DIR.

    Raises:
        None.

    Notes:
        The result includes all files in the cache directory, irrespective of
        extension or format.
    """
    base_dir = ensure_cache_dir()
    files = list(base_dir.glob("*"))
    logger.info("📦 Found %d cached file(s).", len(files))
    return files


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
    # --- Constants ---
    "CACHE_DIR",
    # --- Cache Directory Management ---
    "ensure_cache_dir",
    "get_cache_path",
    # --- Core Cache Functions ---
    "save_cache",
    "load_cache",
    "clear_cache",
    "list_cache_files",
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
        Self-test entry point for C15_cache_manager.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates cache save, load, list, and clear operations.
    """
    logger.info("🔍 C15_cache_manager self-test started.")

    cache_dir = ensure_cache_dir()
    logger.info("📁 Cache directory in use: %s", cache_dir)

    # Example data for test caches
    sample_data = {
        "user": "gerry",
        "date": as_str(get_today()),
        "value": 123,
    }
    df = pd.DataFrame(
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    )

    # --- Save test caches ---------------------------------------------------------------------------
    save_cache("test_json", sample_data, "json")
    save_cache("test_csv", df, "csv")
    save_cache("test_pickle", df, "pkl")

    # --- Load test caches ---------------------------------------------------------------------------
    json_cache = load_cache("test_json", "json")
    csv_cache = load_cache("test_csv", "csv")
    pkl_cache = load_cache("test_pickle", "pkl")

    logger.info("📥 Loaded JSON cache: %s", json_cache)
    logger.info(
        "📥 Loaded CSV cache shape: %s",
        csv_cache.shape if isinstance(csv_cache, pd.DataFrame) else "N/A",
    )
    logger.info("📥 Loaded PKL cache type: %s", type(pkl_cache).__name__)

    # --- List all cache files -----------------------------------------------------------------------
    files = list_cache_files()
    logger.info("📃 Cache files after save: %s", [file.name for file in files])

    # --- Clear test caches --------------------------------------------------------------------------
    clear_cache("test_json")
    clear_cache("test_csv")
    clear_cache("test_pickle")

    remaining_files = list_cache_files()
    logger.info("📃 Cache files after clear: %s", [file.name for file in remaining_files])

    logger.info("✅ C15_cache_manager self-test completed successfully.")


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()