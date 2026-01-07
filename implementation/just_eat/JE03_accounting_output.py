# ====================================================================================================
# JE03_accounting_output.py
# ----------------------------------------------------------------------------------------------------
# Just Eat Step 3 — Produce Accounting Output
#
# Purpose:
#   - Load the reconciliation output from JE02.
#   - Reorder columns to ACCOUNTING_DF_ORDER for accounting team.
#   - Output final accounting CSV.
#
# Usage:
#   from implementation.just_eat.JE03_accounting_output import run_je_accounting_output
#
#   result = run_je_accounting_output(
#       output_folder=Path("..."),
#       acc_start=date(2025, 11, 1),
#       acc_end=date(2025, 11, 30),
#       stmt_start=date(2025, 11, 4),
#       stmt_end_monday=date(2025, 11, 25),
#       log_callback=print,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-01-07
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
# Note: .parent.parent.parent because this file is in implementation/just_eat/
project_root = str(Path(__file__).resolve().parent.parent.parent)
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

# --- Additional project-level imports (append below this line only) ---------------------------------
from core.C07_datetime_utils import format_date, get_end_of_week
from core.C09_io_utils import read_csv_file, save_dataframe
from core.C06_validation_utils import file_exists

from implementation.I03_project_static_lists import ACCOUNTING_DF_ORDER


# ====================================================================================================
# 3. HELPER FUNCTIONS
# ====================================================================================================

def format_date_for_filename(d: date) -> str:
    """Format a date as YY.MM.DD for use in filenames.

    Args:
        d: Date to format.

    Returns:
        str: Formatted date string (e.g., '25.12.01').
    """
    return d.strftime("%y.%m.%d")


def build_reconciliation_filename(stmt_start: date, stmt_end_monday: date) -> str:
    """Build the reconciliation input filename.

    Args:
        stmt_start: Statement period start date (Monday).
        stmt_end_monday: Statement period end date (Monday).

    Returns:
        str: Filename like '25.12.01 - 25.12.29 - Justeat Reconciliation.csv'.
    """
    start_str = format_date_for_filename(stmt_start)
    end_str = format_date_for_filename(stmt_end_monday)
    return f"{start_str} - {end_str} - Justeat Reconciliation.csv"


def build_accounting_filename(stmt_start: date, stmt_end_monday: date) -> str:
    """Build the accounting output filename.

    Args:
        stmt_start: Statement period start date (Monday).
        stmt_end_monday: Statement period end date (Monday).

    Returns:
        str: Filename like '25.12.01 - 25.12.29 - Justeat Accounting.csv'.
    """
    start_str = format_date_for_filename(stmt_start)
    end_str = format_date_for_filename(stmt_end_monday)
    return f"{start_str} - {end_str} - Justeat Accounting.csv"


# ====================================================================================================
# 4. MAIN ACCOUNTING OUTPUT FUNCTION
# ====================================================================================================

def run_je_accounting_output(
    output_folder: Path,
    acc_start: date,
    acc_end: date,
    stmt_start: date,
    stmt_end_monday: date,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """Run the Just Eat accounting output generation process.

    Description:
        Loads the reconciliation CSV from JE02, reorders columns to match
        ACCOUNTING_DF_ORDER, and saves as the accounting output CSV.

    Args:
        output_folder: Folder containing reconciliation CSV and for output.
        acc_start: Accounting period start.
        acc_end: Accounting period end.
        stmt_start: Statement period start (Monday).
        stmt_end_monday: Statement period end (Monday).
        log_callback: Optional callback for GUI logging.

    Returns:
        Path | None: Path to the output CSV, or None if generation fails.

    Notes:
        - Requires JE02 reconciliation output to exist.
        - Columns not in ACCOUNTING_DF_ORDER are dropped.
        - Columns in ACCOUNTING_DF_ORDER but missing from data are skipped.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Calculate Sunday end date from Monday (for display/logging only)
    stmt_end_sunday = get_end_of_week(stmt_end_monday)

    log("=" * 60)
    log("JUST EAT ACCOUNTING OUTPUT")
    log("=" * 60)
    log(f"Accounting Period: {acc_start} -> {acc_end}")
    log(f"Statement Period: {stmt_start} -> {stmt_end_sunday}")

    # 1. Build input filename and check it exists (uses Monday dates)
    recon_filename = build_reconciliation_filename(stmt_start, stmt_end_monday)
    recon_path = output_folder / recon_filename

    log(f"Looking for: {recon_filename}")

    if not file_exists(recon_path):
        log(f"ERROR: Reconciliation file not found: {recon_path}")
        raise FileNotFoundError(f"Reconciliation file not found: {recon_path}")

    # 2. Load reconciliation CSV
    log(f"Loading reconciliation file...")
    df = read_csv_file(recon_path)
    log(f"Loaded {len(df):,} rows, {len(df.columns)} columns")

    # 3. Reorder columns to ACCOUNTING_DF_ORDER
    # Only include columns that exist in both the data and the order list
    available_columns = [col for col in ACCOUNTING_DF_ORDER if col in df.columns]
    missing_columns = [col for col in ACCOUNTING_DF_ORDER if col not in df.columns]

    if missing_columns:
        log(f"Note: {len(missing_columns)} columns from ACCOUNTING_DF_ORDER not in data (skipped)")
        logger.debug(f"Missing columns: {missing_columns}")

    df_reordered = df[available_columns].copy()
    log(f"Reordered to {len(available_columns)} columns (ACCOUNTING_DF_ORDER)")

    # 4. Build output filename and save (uses Monday dates)
    accounting_filename = build_accounting_filename(stmt_start, stmt_end_monday)
    accounting_path = output_folder / accounting_filename

    log(f"Saving: {accounting_filename}")
    save_dataframe(df_reordered, accounting_path, index=False, backup_existing=False)

    log(f"Saved {len(df_reordered):,} rows to {accounting_path.name}")
    log("=" * 60)

    return accounting_path


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
__all__ = [
    "run_je_accounting_output",
]


# ====================================================================================================
# 99. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
def main() -> None:
    """Self-test for JE03_accounting_output module.

    Description:
        Provides usage information when run directly.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - For actual testing, call run_je_accounting_output() with appropriate parameters.
    """
    logger.info("=" * 60)
    logger.info("JE03_accounting_output.py - Self Test")
    logger.info("=" * 60)
    logger.info("This module should be called via G10b controller or run_je_accounting_output().")
    logger.info("For testing, provide output_folder and date parameters.")
    logger.info("")
    logger.info("ACCOUNTING_DF_ORDER has %d columns:", len(ACCOUNTING_DF_ORDER))
    for i, col in enumerate(ACCOUNTING_DF_ORDER, 1):
        logger.info("  %2d. %s", i, col)


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()
