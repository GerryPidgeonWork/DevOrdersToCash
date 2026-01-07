# ====================================================================================================
# DR02_data_reconciliation.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo Step 2 - Data Reconciliation
#
# Purpose:
#   - Load DWH data (filtered by order_vendor = 'Deliveroo').
#   - Load Deliveroo Combined CSV (from DR01).
#   - Match orders using composite key: last 4 digits of order_number + mfc_name + date (+/-1 day).
#   - Output reconciliation CSV with match statistics.
#
# Matching Logic:
#   - Deliveroo: last 4 digits of `order_number` + `mfc_name` + `delivery_datetime_utc`
#   - DWH: `mp_order_id` + `location_name` + `created_at_day` (within +/-1 day)
#
# Field Mapping (Variance Calculation):
#   - Deliveroo reports original order value + separate refund adjustments for unavailable items
#   - DWH records the NET fulfilled value (already excluding unavailable items)
#   - Orders are grouped by order_number before matching:
#       gross_order_value = order_value_gross + marketing_offer_discount
#       net_sales_value = gross_order_value + unavailable_items_adjustment
#   - net_sales_value is compared against DWH post_promo_sales_inc_vat
#   - DWH bag fee is captured separately in `mp_bag_fee_inc_vat` (not in Deliveroo order value)
#
# Order Categories:
#   - "Matched": Order matched DWH (no adjustments needed)
#   - "Matched (Grouped)": Order matched after including refund adjustments
#   - "Linked to Order": Additional Fees/Payments row linked to a matched order
#   - "Not Matched": Order with no DWH match
#   - "Standalone Adjustment": Additional Fees/Payments with no parent order
#
# Usage:
#   from implementation.deliveroo.DR02_data_reconciliation import run_dr_reconciliation
#
#   result = run_dr_reconciliation(
#       dwh_folder=Path("..."),
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
# Created:      2025-12-13
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
# Note: .parent.parent.parent because this file is in implementation/deliveroo/
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
from core.C06_validation_utils import validate_directory_exists, file_exists
from core.C07_datetime_utils import format_date
from core.C09_io_utils import read_csv_file, save_dataframe
from core.C12_data_processing import standardise_columns, convert_to_datetime

from implementation.I02_project_shared_functions import calculate_accrual_period


# ====================================================================================================
# 3. DWH LOADING (DELIVEROO ONLY)
# ====================================================================================================

def load_dwh_deliveroo(
    dwh_folder: Path,
    start_date: date,
    end_date: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load DWH data filtered by order_vendor = 'Deliveroo'.

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        start_date (date): Period start date.
        end_date (date): Period end date.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Combined Deliveroo DWH data.

    Raises:
        FileNotFoundError: If no DWH files found.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    validate_directory_exists(dwh_folder)

    csv_files = list(dwh_folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No DWH CSV files found in {dwh_folder}")

    dfs = []
    for csv_file in csv_files:
        try:
            df = read_csv_file(csv_file, dtype=str, low_memory=False)
            dfs.append(df)
            logger.debug(f"Loaded: {csv_file.name} ({len(df):,} rows)")
        except Exception as e:
            logger.warning(f"Skipped {csv_file.name}: {e}")

    if not dfs:
        raise FileNotFoundError(f"No valid DWH CSV files in {dwh_folder}")

    combined = pd.concat(dfs, ignore_index=True)
    log(f"Loaded {len(csv_files)} DWH file(s) -> {len(combined):,} total rows")

    # Standardise column names
    combined = standardise_columns(combined)

    # Filter to Deliveroo orders only
    if "order_vendor" in combined.columns:
        combined = combined[combined["order_vendor"].str.lower() == "deliveroo"].copy()
        log(f"Filtered to Deliveroo: {len(combined):,} rows")
    else:
        log("Warning: No order_vendor column found - using all rows")

    # Clean mp_order_id (this is the last 4 digits we match against)
    if "mp_order_id" in combined.columns:
        combined["mp_order_id"] = (
            combined["mp_order_id"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"[^0-9]", "", regex=True)
        )

    # Convert numeric columns
    numeric_cols = [
        "order_completed",
        "total_payment_with_tips_inc_vat",
        "total_payment_inc_vat",
        "post_promo_sales_inc_vat",
        "delivery_fee_inc_vat",
        "priority_fee_inc_vat",
        "small_order_fee_inc_vat",
        "mp_bag_fee_inc_vat",
        "tips_amount",
    ]
    for col in numeric_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0.0)

    # Convert date columns
    if "created_at_day" in combined.columns:
        combined = convert_to_datetime(combined, ["created_at_day"])
        combined["created_at_day"] = combined["created_at_day"].dt.date

    # Parse timestamp columns for collision resolution
    if "created_at_timestamp" in combined.columns:
        combined["created_at_ts"] = pd.to_datetime(combined["created_at_timestamp"], errors="coerce")
    if "delivered_at_timestamp" in combined.columns:
        combined["delivered_at_ts"] = pd.to_datetime(combined["delivered_at_timestamp"], errors="coerce")

    return combined


# ====================================================================================================
# 4. DELIVEROO COMBINED CSV LOADING
# ====================================================================================================

def load_dr_combined(
    output_folder: Path,
    stmt_start: date,
    stmt_end_sunday: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load the Deliveroo Combined CSV produced by DR01.

    Args:
        output_folder (Path): Folder containing the CSV.
        stmt_start (date): Statement period start.
        stmt_end_sunday (date): Statement period end (Sunday).
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Deliveroo combined data.

    Raises:
        FileNotFoundError: If expected file not found.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Build expected filename pattern
    start_str = format_date(stmt_start, "%y.%m.%d")
    end_str = format_date(stmt_end_sunday, "%y.%m.%d")
    expected_filename = f"{start_str} - {end_str} - Deliveroo Combined.csv"
    dr_file = output_folder / expected_filename

    if not file_exists(dr_file):
        # Try to find a Deliveroo Combined file that starts with the same date
        pattern = f"{start_str} - * - Deliveroo Combined.csv"
        matching_files = sorted(output_folder.glob(pattern), reverse=True)

        if matching_files:
            # Use the most recent matching file
            dr_file = matching_files[0]
            log(f"Using available file: {dr_file.name} (expected: {expected_filename})")
        else:
            # No matching files found
            available = [f.name for f in output_folder.glob("*Deliveroo Combined*.csv")]
            raise FileNotFoundError(
                f"Missing Deliveroo Combined file: {expected_filename}\n"
                f"Available files: {', '.join(available) or 'None'}\n"
                f"Please run Step 1 (Parse CSVs) first."
            )

    dr_df = read_csv_file(dr_file, low_memory=False)
    log(f"Loaded Deliveroo data: {dr_file.name} -> {len(dr_df):,} rows")

    # Ensure numeric columns (including marketing_offer_discount for variance calculation)
    numeric_cols = [
        "order_value_gross", "commission_net", "commission_vat",
        "adjustment_net", "adjustment_vat", "total_payable",
        "marketing_offer_discount",
    ]
    for col in numeric_cols:
        if col in dr_df.columns:
            dr_df[col] = pd.to_numeric(dr_df[col], errors="coerce").fillna(0)

    # Calculate gross totals (net + vat) for easier reconciliation
    if "commission_net" in dr_df.columns and "commission_vat" in dr_df.columns:
        dr_df["commission_gross"] = dr_df["commission_net"] + dr_df["commission_vat"]

    if "adjustment_net" in dr_df.columns and "adjustment_vat" in dr_df.columns:
        dr_df["adjustment_gross"] = dr_df["adjustment_net"] + dr_df["adjustment_vat"]

    # Extract last 4 digits of order_number for matching
    # Strip leading zeros to match DWH format (e.g., "0660" -> "660")
    if "order_number" in dr_df.columns:
        dr_df["order_last4"] = (
            dr_df["order_number"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str[-4:]  # Last 4 digits
            .str.lstrip("0")  # Strip leading zeros to match DWH format
        )
        # Handle edge case where order ends in "0000" -> becomes empty string
        dr_df.loc[dr_df["order_last4"] == "", "order_last4"] = "0"
        log(f"Extracted last 4 digits from order_number (leading zeros stripped)")

    # Convert delivery_datetime_utc to date and timestamp for matching
    # Format is already string datetime like "2025-10-27 00:09:20"
    if "delivery_datetime_utc" in dr_df.columns:
        dr_df["dr_delivery_ts"] = pd.to_datetime(
            dr_df["delivery_datetime_utc"],
            errors='coerce'
        )
        dr_df["delivery_date"] = dr_df["dr_delivery_ts"].dt.date

    return dr_df


# ====================================================================================================
# 5. ORDER AGGREGATION (GROUP ORDERS WITH ADJUSTMENTS)
# ====================================================================================================

def aggregate_order_values(dr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Group Deliveroo rows by order_number and calculate net values.

        For each unique order_number, calculates:
        - gross_order_value: order_value_gross + marketing_offer_discount (from "Order Value & Commission" row)
        - unavailable_items_adjustment: sum(adjustment_gross) WHERE accounting_category = 'Additional Fees'
        - net_sales_value: gross_order_value + unavailable_items_adjustment

        Note: "Additional Payments" (commission refunds) do NOT affect sales value reconciliation.
        They represent commission adjustments, not changes to the customer order value.

    Args:
        dr_df (pd.DataFrame): Deliveroo Combined data with all row types.

    Returns:
        pd.DataFrame: Aggregated data with one row per order_number containing:
            - order_number
            - order_last4 (for matching)
            - mfc_name (for matching)
            - delivery_date (for matching)
            - gross_order_value
            - unavailable_items_adjustment
            - net_sales_value (this is what we compare to DWH)
            - order_row_count (how many DR rows for this order)
            - has_refund (boolean - True if any Additional Fees rows exist)
    """
    # Separate order types
    orders_df = dr_df[dr_df["accounting_category"] == "Order Value & Commission"].copy()
    fees_df = dr_df[dr_df["accounting_category"] == "Additional Fees"].copy()

    if orders_df.empty:
        return pd.DataFrame()

    # Calculate gross_order_value for each order
    orders_df["marketing_offer_discount"] = pd.to_numeric(
        orders_df.get("marketing_offer_discount", 0), errors="coerce"
    ).fillna(0)
    orders_df["order_value_gross"] = pd.to_numeric(
        orders_df["order_value_gross"], errors="coerce"
    ).fillna(0)
    orders_df["gross_order_value"] = orders_df["order_value_gross"] + orders_df["marketing_offer_discount"]

    # Aggregate Additional Fees adjustments by order_number
    # These are typically refunds for unavailable items (negative values)
    if not fees_df.empty:
        fees_df["adjustment_gross"] = pd.to_numeric(
            fees_df.get("adjustment_gross", 0), errors="coerce"
        ).fillna(0)

        fees_agg = fees_df.groupby("order_number").agg(
            unavailable_items_adjustment=("adjustment_gross", "sum"),
            fees_row_count=("order_number", "count"),
        ).reset_index()
    else:
        fees_agg = pd.DataFrame(columns=["order_number", "unavailable_items_adjustment", "fees_row_count"])
        fees_agg["unavailable_items_adjustment"] = 0
        fees_agg["fees_row_count"] = 0

    # Count total rows per order_number (orders + adjustments)
    row_counts = dr_df.groupby("order_number").size().reset_index(name="order_row_count")

    # Build aggregated result from orders
    agg_df = orders_df[[
        "order_number", "order_last4", "mfc_name", "delivery_date",
        "gross_order_value", "order_value_gross", "marketing_offer_discount"
    ]].copy()

    # Merge in adjustments
    agg_df = agg_df.merge(fees_agg, on="order_number", how="left")
    agg_df["unavailable_items_adjustment"] = agg_df["unavailable_items_adjustment"].fillna(0)
    agg_df["fees_row_count"] = agg_df["fees_row_count"].fillna(0).astype(int)

    # Merge row counts
    agg_df = agg_df.merge(row_counts, on="order_number", how="left")

    # Calculate net_sales_value (what we compare to DWH)
    # DWH records the net fulfilled value, so we need: gross - refunds
    agg_df["net_sales_value"] = agg_df["gross_order_value"] + agg_df["unavailable_items_adjustment"]

    # Flag orders with refunds
    agg_df["has_refund"] = agg_df["unavailable_items_adjustment"] != 0

    return agg_df


# ====================================================================================================
# 6. MATCHING LOGIC
# ====================================================================================================

def _resolve_collision_by_timestamp(
    dr_delivery_ts: Any,
    candidates: List[Dict],
    buffer_hours: int = 1,
) -> Tuple[Dict | None, str]:
    """
    Resolve collision using timestamp window.

    DR delivery_datetime_utc must fall between:
      - DWH created_at_timestamp
      - DWH delivered_at_timestamp + buffer

    Args:
        dr_delivery_ts: Deliveroo delivery timestamp.
        candidates: List of DWH candidate dicts with timestamps.
        buffer_hours: Buffer after delivered_at_timestamp.

    Returns:
        tuple: (matched_candidate, match_type) or (None, reason)
    """
    if pd.isna(dr_delivery_ts):
        return None, "NO_DR_TIMESTAMP"

    matching_candidates = []

    for cand in candidates:
        created_ts = cand.get("created_at_ts")
        delivered_ts = cand.get("delivered_at_ts")

        if pd.isna(created_ts) or pd.isna(delivered_ts):
            continue

        # Window: created_at to delivered_at + buffer
        window_end = delivered_ts + timedelta(hours=buffer_hours)

        if created_ts <= dr_delivery_ts <= window_end:
            matching_candidates.append(cand)

    if len(matching_candidates) == 1:
        return matching_candidates[0], "MATCHED_BY_TIMESTAMP"
    elif len(matching_candidates) > 1:
        return None, "MULTIPLE_TIMESTAMP_MATCHES"
    else:
        return None, "NO_TIMESTAMP_MATCH"


def _resolve_collision_by_value(
    dr_value: float,
    candidates: List[Dict],
    tolerance: float = 0.10,
) -> Tuple[Dict | None, str]:
    """
    Resolve collision by matching closest value.
    Used as fallback when timestamp resolution fails.

    Args:
        dr_value: Deliveroo net_sales_value.
        candidates: List of DWH candidate dicts with dwh_value.
        tolerance: Maximum absolute difference for match (default £0.10).

    Returns:
        tuple: (matched_candidate, match_type) or (None, reason)
    """
    if pd.isna(dr_value):
        return None, "NO_DR_VALUE"

    best_match = None
    best_diff = float("inf")

    for cand in candidates:
        dwh_value = cand.get("dwh_value", 0) or 0
        diff = abs(dwh_value - dr_value)

        if diff < best_diff:
            best_diff = diff
            best_match = cand

    if best_match:
        dwh_value = best_match.get("dwh_value", 0) or 0
        # Check if it's a good match (within tolerance or 1% of value)
        if best_diff < tolerance or (dwh_value > 0 and best_diff / dwh_value < 0.01):
            return best_match, "MATCHED_BY_VALUE"

    return None, "NO_VALUE_MATCH"


def match_deliveroo_orders(
    dr_df: pd.DataFrame,
    dwh_df: pd.DataFrame,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Match Deliveroo orders with DWH using robust 4-step matching:
        1. Direct match (same date)
        2. Cross-midnight match (previous day)
        3. Timestamp resolution for collisions
        4. Value-based fallback for remaining collisions

    Features:
        - Strips leading zeros from order_last4 to match DWH format
        - Groups orders with their related adjustments
        - Tracks matched DWH records to prevent duplicate matches
        - Sorts orders by timestamp (earliest first) for consistent matching

    Match Categories:
        - "MATCHED": Single DWH candidate on same date
        - "MATCHED_CROSS_MIDNIGHT": Single candidate on previous day
        - "MATCHED_BY_TIMESTAMP": Collision resolved by timestamp window
        - "MATCHED_BY_VALUE": Collision resolved by value matching
        - "NO_DWH_RECORD": No candidate found (checked both dates)
        - "COLLISION": Could not resolve (should be 0 with this logic)

    Order Categories (for row types):
        - "Matched": Order matched DWH (no adjustments)
        - "Matched (Grouped)": Order matched after including refund adjustments
        - "Linked to Order": Additional Fees/Payments linked to matched order
        - "Not Matched": Order with no DWH match
        - "Standalone Adjustment": Adjustment with no parent order

    Args:
        dr_df (pd.DataFrame): Deliveroo Combined data.
        dwh_df (pd.DataFrame): DWH Deliveroo data.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: All original rows with match results and DWH data propagated.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # -----------------------------------------------------------------------------------------
    # Step 1: Categorise Deliveroo rows
    # -----------------------------------------------------------------------------------------
    if "accounting_category" not in dr_df.columns:
        dr_df["accounting_category"] = "Order Value & Commission"

    orders_df = dr_df[dr_df["accounting_category"] == "Order Value & Commission"].copy()
    fees_df = dr_df[dr_df["accounting_category"] == "Additional Fees"].copy()
    payments_df = dr_df[dr_df["accounting_category"] == "Additional Payments"].copy()

    log(f"Deliveroo breakdown: {len(orders_df):,} orders, {len(fees_df):,} fees, {len(payments_df):,} payments")

    # Prepare DWH for matching - only completed orders
    dwh_completed = dwh_df[dwh_df["order_completed"] == 1].copy()
    log(f"DWH completed Deliveroo orders: {len(dwh_completed):,}")

    if orders_df.empty:
        log("Warning: No order rows found")
        dr_df["order_category"] = "No Orders"
        dr_df["match_status"] = "N/A"
        return dr_df

    # -----------------------------------------------------------------------------------------
    # Step 2: Aggregate orders with their adjustments
    # -----------------------------------------------------------------------------------------
    agg_df = aggregate_order_values(dr_df)
    orders_with_refunds = (agg_df["has_refund"] == True).sum()
    log(f"Aggregated to {len(agg_df):,} unique orders ({orders_with_refunds:,} with refund adjustments)")

    if "order_last4" not in agg_df.columns:
        log("Warning: order_last4 column missing - cannot match")
        dr_df["order_category"] = "No Match Key"
        dr_df["match_status"] = "N/A"
        return dr_df

    # Get delivery timestamps from original orders for collision resolution
    order_timestamps = orders_df.set_index("order_number")["dr_delivery_ts"].to_dict()

    # -----------------------------------------------------------------------------------------
    # Step 3: Build DWH lookup with timestamps for collision resolution
    # Key: (last4, mfc, date) -> list of dicts with gp_order_id, dwh_value, timestamps
    # -----------------------------------------------------------------------------------------
    dwh_lookup: Dict[Tuple[str, str, Any], List[Dict]] = {}

    for idx, row in dwh_completed.iterrows():
        mp_id = str(row.get("mp_order_id", "")).strip()
        loc = str(row.get("location_name", "")).strip()
        order_date = row.get("created_at_day")
        dwh_value = float(row.get("post_promo_sales_inc_vat", 0) or 0)
        gp_order_id = row.get("gp_order_id")
        created_at_ts = row.get("created_at_ts")
        delivered_at_ts = row.get("delivered_at_ts")

        if mp_id and loc and mp_id != "nan":
            key = (mp_id, loc, order_date)
            if key not in dwh_lookup:
                dwh_lookup[key] = []
            dwh_lookup[key].append({
                "idx": idx,
                "gp_order_id": gp_order_id,
                "dwh_value": dwh_value,
                "created_at_ts": created_at_ts,
                "delivered_at_ts": delivered_at_ts,
            })

    # Count single vs multiple candidates
    single_cand = sum(1 for v in dwh_lookup.values() if len(v) == 1)
    multi_cand = sum(1 for v in dwh_lookup.values() if len(v) > 1)
    log(f"Built DWH lookup: {len(dwh_lookup):,} keys ({single_cand:,} single, {multi_cand:,} potential collisions)")

    # -----------------------------------------------------------------------------------------
    # Step 4: Match aggregated orders to DWH with 4-step priority
    # Sort by delivery timestamp (earliest first) for consistent matching
    # -----------------------------------------------------------------------------------------
    agg_df_sorted = agg_df.sort_values("delivery_date").copy()

    match_results: Dict[str, Dict] = {}  # order_number -> match info
    used_dwh_ids: set = set()  # Track matched gp_order_ids to prevent duplicates

    stats = {
        "matched_direct": 0,
        "matched_cross_midnight": 0,
        "matched_by_timestamp": 0,
        "matched_by_value": 0,
        "no_dwh_record": 0,
        "collision": 0,
        "matched_grouped": 0,
    }

    for _, agg_row in agg_df_sorted.iterrows():
        order_num = str(agg_row.get("order_number", ""))
        dr_last4 = str(agg_row.get("order_last4", "")).strip()
        dr_mfc = str(agg_row.get("mfc_name", "")).strip()
        dr_date = agg_row.get("delivery_date")
        net_value = float(agg_row.get("net_sales_value", 0) or 0)
        has_refund = agg_row.get("has_refund", False)
        dr_ts = order_timestamps.get(agg_row.get("order_number"))

        matched_candidate = None
        match_status = None
        cross_midnight = False

        # Get candidates for same date
        key = (dr_last4, dr_mfc, dr_date)
        candidates = dwh_lookup.get(key, [])

        # Filter out already-used DWH records
        available = [c for c in candidates if c["gp_order_id"] not in used_dwh_ids]

        # If no match on same date, try previous day (cross-midnight)
        if not available and dr_date is not None:
            prev_date = dr_date - timedelta(days=1)
            prev_key = (dr_last4, dr_mfc, prev_date)
            prev_candidates = dwh_lookup.get(prev_key, [])
            available = [c for c in prev_candidates if c["gp_order_id"] not in used_dwh_ids]
            if available:
                cross_midnight = True

        # Matching logic with priority
        if not available:
            # No candidates found
            match_status = "NO_DWH_RECORD"
            stats["no_dwh_record"] += 1
        elif len(available) == 1:
            # Single candidate - direct match
            matched_candidate = available[0]
            if cross_midnight:
                match_status = "MATCHED_CROSS_MIDNIGHT"
                stats["matched_cross_midnight"] += 1
            else:
                match_status = "MATCHED"
                stats["matched_direct"] += 1
        else:
            # Multiple candidates - try timestamp resolution
            matched_candidate, ts_result = _resolve_collision_by_timestamp(dr_ts, available)

            if matched_candidate:
                match_status = "MATCHED_BY_TIMESTAMP"
                stats["matched_by_timestamp"] += 1
            else:
                # Timestamp failed - try value matching
                matched_candidate, val_result = _resolve_collision_by_value(net_value, available)

                if matched_candidate:
                    match_status = "MATCHED_BY_VALUE"
                    stats["matched_by_value"] += 1
                else:
                    # Could not resolve collision
                    match_status = "COLLISION"
                    stats["collision"] += 1

        # Derive match_confidence from match_status
        confidence_map = {
            "MATCHED": "High",
            "MATCHED_CROSS_MIDNIGHT": "High (Cross-Midnight)",
            "MATCHED_BY_TIMESTAMP": "Medium (Timestamp)",
            "MATCHED_BY_VALUE": "Low (Value)",
            "NO_DWH_RECORD": "N/A",
            "COLLISION": "Ambiguous",
        }
        match_confidence = confidence_map.get(match_status, "Unknown")

        # Store match result
        if matched_candidate is not None:
            dwh_idx = matched_candidate["idx"]
            dwh_row = dwh_completed.loc[dwh_idx]
            order_category = "Matched (Grouped)" if has_refund else "Matched"
            if has_refund:
                stats["matched_grouped"] += 1

            # Mark this DWH record as used
            used_dwh_ids.add(matched_candidate["gp_order_id"])

            match_results[order_num] = {
                "matched": True,
                "dwh_idx": dwh_idx,
                "dwh_data": {f"dwh_{col}": dwh_row[col] for col in dwh_row.index},
                "order_category": order_category,
                "match_status": match_status,
                "match_confidence": match_confidence,
                "cross_midnight": cross_midnight,
                "net_sales_value": net_value,
                "gross_order_value": float(agg_row.get("gross_order_value", 0) or 0),
                "unavailable_items_adjustment": float(agg_row.get("unavailable_items_adjustment", 0) or 0),
            }
        else:
            match_results[order_num] = {
                "matched": False,
                "order_category": "Not Matched",
                "match_status": match_status,
                "match_confidence": match_confidence,
                "cross_midnight": cross_midnight,
                "net_sales_value": net_value,
                "gross_order_value": float(agg_row.get("gross_order_value", 0) or 0),
                "unavailable_items_adjustment": float(agg_row.get("unavailable_items_adjustment", 0) or 0),
            }

    # Log matching statistics
    total_matched = stats["matched_direct"] + stats["matched_cross_midnight"] + stats["matched_by_timestamp"] + stats["matched_by_value"]
    log(f"Matching results: {total_matched:,} matched, {stats['no_dwh_record']:,} no DWH record")
    log(f"   MATCHED (direct): {stats['matched_direct']:,}")
    log(f"   MATCHED_CROSS_MIDNIGHT: {stats['matched_cross_midnight']:,}")
    log(f"   MATCHED_BY_TIMESTAMP: {stats['matched_by_timestamp']:,}")
    log(f"   MATCHED_BY_VALUE: {stats['matched_by_value']:,}")
    log(f"   COLLISION (unresolved): {stats['collision']:,}")
    log(f"   Matched with refund adjustments: {stats['matched_grouped']:,}")
    log(f"   DWH records used: {len(used_dwh_ids):,}")

    # -----------------------------------------------------------------------------------------
    # Step 5: Propagate match results back to ALL original rows
    # -----------------------------------------------------------------------------------------
    result_rows = []

    for _, dr_row in dr_df.iterrows():
        row_dict = dr_row.to_dict()
        order_num = str(dr_row.get("order_number", ""))
        accounting_cat = dr_row.get("accounting_category", "")

        if order_num in match_results:
            match_info = match_results[order_num]

            # Add aggregated values
            row_dict["net_sales_value"] = match_info["net_sales_value"]
            row_dict["gross_order_value"] = match_info["gross_order_value"]
            row_dict["unavailable_items_adjustment"] = match_info["unavailable_items_adjustment"]

            if match_info["matched"]:
                # Add DWH data
                row_dict.update(match_info["dwh_data"])

                # Set category based on row type
                if accounting_cat == "Order Value & Commission":
                    row_dict["order_category"] = match_info["order_category"]
                    row_dict["match_status"] = match_info["match_status"]
                    row_dict["match_confidence"] = match_info["match_confidence"]
                else:
                    # Additional Fees/Payments linked to matched order
                    row_dict["order_category"] = "Linked to Order"
                    row_dict["match_status"] = "LINKED"
                    row_dict["match_confidence"] = "Inherited"
            else:
                row_dict["order_category"] = "Not Matched" if accounting_cat == "Order Value & Commission" else "Linked to Unmatched"
                row_dict["match_status"] = match_info["match_status"]
                row_dict["match_confidence"] = match_info["match_confidence"]
        else:
            # Standalone adjustment (order_number = 0 or not in orders)
            row_dict["order_category"] = "Standalone Adjustment"
            row_dict["match_status"] = "N/A"
            row_dict["match_confidence"] = "N/A"
            row_dict["net_sales_value"] = 0
            row_dict["gross_order_value"] = 0
            row_dict["unavailable_items_adjustment"] = 0

        result_rows.append(row_dict)

    result_df = pd.DataFrame(result_rows)

    # -----------------------------------------------------------------------------------------
    # Step 6: Post-match quality check for high-variance matches
    # -----------------------------------------------------------------------------------------
    if "dwh_post_promo_sales_inc_vat" in result_df.columns:
        matched_mask = result_df["order_category"].isin(["Matched", "Matched (Grouped)"])

        net_val = pd.to_numeric(result_df["net_sales_value"], errors="coerce").fillna(0)
        dwh_val = pd.to_numeric(result_df["dwh_post_promo_sales_inc_vat"], errors="coerce").fillna(0)

        variance_pct = np.where(
            net_val > 0,
            np.abs(net_val - dwh_val) / net_val * 100,
            0
        )

        high_variance_mask = matched_mask & (variance_pct > 20)
        result_df.loc[high_variance_mask, "match_confidence"] = (
            result_df.loc[high_variance_mask, "match_confidence"] + " - Review"
        )

        review_count = high_variance_mask.sum()
        if review_count > 0:
            log(f"   Flagged for review (>20% variance): {review_count:,}")

    return result_df


# ====================================================================================================
# 7. VARIANCE CALCULATION
# ====================================================================================================

def calculate_variances(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Calculate variance between Deliveroo net_sales_value (grouped) and DWH post_promo_sales_inc_vat.

        Field Mapping:
            - net_sales_value = gross_order_value + unavailable_items_adjustment
            - gross_order_value = order_value_gross + marketing_offer_discount
            - DWH records net fulfilled value (already excluding unavailable items)
            - DWH bag fee is captured separately in dwh_mp_bag_fee_inc_vat

        Variance Explanations:
            - "Exact Match": variance < £0.02
            - "Rounding": variance < £0.10
            - "Minor Variance": variance < £1.00
            - "Unexplained Variance": variance >= £1.00

    Args:
        df (pd.DataFrame): Reconciliation data with net_sales_value from grouped matching.

    Returns:
        pd.DataFrame: Data with variance columns added.
    """
    df = df.copy()

    # Calculate variance for matched orders (both simple and grouped matches)
    matched_mask = df["order_category"].isin(["Matched", "Matched (Grouped)"])

    # net_sales_value is already calculated during matching
    # It equals: gross_order_value + unavailable_items_adjustment
    # where gross_order_value = order_value_gross + marketing_offer_discount

    if "dwh_post_promo_sales_inc_vat" in df.columns and "net_sales_value" in df.columns:
        # Calculate variance
        net_val = pd.to_numeric(df["net_sales_value"], errors="coerce").fillna(0)
        dwh_val = pd.to_numeric(df["dwh_post_promo_sales_inc_vat"], errors="coerce").fillna(0)

        df["amount_variance"] = (net_val.round(2) - dwh_val.round(2)).round(2)

        # Classify variance for matched rows
        abs_variance = df["amount_variance"].abs()

        # Initialize columns
        df["matched_amount"] = "N/A"
        df["variance_explanation"] = "N/A"

        # Exact match (< £0.02)
        exact_mask = matched_mask & (abs_variance < 0.02)
        df.loc[exact_mask, "matched_amount"] = "Exact Match"
        df.loc[exact_mask, "variance_explanation"] = "Exact Match"

        # Rounding (£0.02 - £0.10)
        rounding_mask = matched_mask & (abs_variance >= 0.02) & (abs_variance < 0.10)
        df.loc[rounding_mask, "matched_amount"] = "Exact Match"  # Still consider matched
        df.loc[rounding_mask, "variance_explanation"] = "Rounding"

        # Minor variance (£0.10 - £1.00)
        minor_mask = matched_mask & (abs_variance >= 0.10) & (abs_variance < 1.00)
        df.loc[minor_mask, "matched_amount"] = "Minor Variance"
        df.loc[minor_mask, "variance_explanation"] = "Minor Variance"

        # Unexplained variance (>= £1.00)
        unexplained_mask = matched_mask & (abs_variance >= 1.00)
        df.loc[unexplained_mask, "matched_amount"] = "Value Variance"
        df.loc[unexplained_mask, "variance_explanation"] = "Unexplained Variance"

        # Linked rows inherit parent's variance
        linked_mask = df["order_category"] == "Linked to Order"
        df.loc[linked_mask, "matched_amount"] = "Linked"
        df.loc[linked_mask, "variance_explanation"] = "See Parent Order"

    else:
        df["amount_variance"] = 0
        df["matched_amount"] = "No DWH Value"
        df["variance_explanation"] = "N/A"

    # Set for non-matched/non-linked rows
    non_matched_mask = ~df["order_category"].isin(["Matched", "Matched (Grouped)", "Linked to Order"])
    df.loc[non_matched_mask, "amount_variance"] = 0

    return df


# ====================================================================================================
# 8. MAIN RECONCILIATION FUNCTION
# ====================================================================================================

def run_dr_reconciliation(
    dwh_folder: Path,
    output_folder: Path,
    acc_start: date,
    acc_end: date,
    stmt_start: date,
    stmt_end_sunday: date,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """
    Description:
        Run the full Deliveroo reconciliation process.

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        output_folder (Path): Folder for output (also contains Deliveroo Combined).
        acc_start (date): Accounting period start.
        acc_end (date): Accounting period end.
        stmt_start (date): Statement period start (Monday).
        stmt_end_sunday (date): Statement period end (Sunday).
        log_callback (Callable | None): Optional callback for GUI logging.

    Returns:
        Path | None: Path to the output CSV, or None if reconciliation fails.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log("=" * 60)
    log("DELIVEROO RECONCILIATION")
    log("=" * 60)
    log(f"Accounting Period: {acc_start} -> {acc_end}")
    log(f"Statement Period: {stmt_start} -> {stmt_end_sunday}")

    # Calculate accrual period
    accrual_start, accrual_end = calculate_accrual_period(acc_end, stmt_end_sunday)
    if accrual_start:
        log(f"Accrual Period: {accrual_start} -> {accrual_end}")
    else:
        log("Accrual Period: Not needed")

    try:
        # 1) Load DWH data (Deliveroo only)
        log("")
        log("Step 1: Load DWH Data (Deliveroo)")
        dwh_df = load_dwh_deliveroo(dwh_folder, acc_start, acc_end, log_callback)

        # 2) Load Deliveroo Combined CSV
        log("")
        log("Step 2: Load Deliveroo Combined CSV")
        dr_df = load_dr_combined(output_folder, stmt_start, stmt_end_sunday, log_callback)

        # 3) Match orders
        log("")
        log("Step 3: Match Deliveroo with DWH")
        merged_df = match_deliveroo_orders(dr_df, dwh_df, log_callback)

        # 4) Calculate variances
        log("")
        log("Step 4: Calculate Variances")
        final_df = calculate_variances(merged_df)

        # 5) Summary statistics
        log("")
        log("=" * 60)
        log("RECONCILIATION SUMMARY")
        log("=" * 60)

        # Row category breakdown
        log("")
        log("Row Categories:")
        category_order = ["Matched", "Matched (Grouped)", "Linked to Order", "Not Matched",
                         "Linked to Unmatched", "Standalone Adjustment"]
        for cat in category_order:
            if cat in final_df["order_category"].values:
                count = (final_df["order_category"] == cat).sum()
                log(f"   {cat}: {count:,}")

        # Grouped matching statistics
        log("")
        log("Grouping Statistics:")
        order_mask = final_df["accounting_category"] == "Order Value & Commission"
        matched_simple = (final_df["order_category"] == "Matched").sum()
        matched_grouped = (final_df["order_category"] == "Matched (Grouped)").sum()
        total_orders = order_mask.sum()
        orders_with_adjustments = matched_grouped

        if orders_with_adjustments > 0:
            log(f"   Orders with refund adjustments: {orders_with_adjustments:,}")
            log(f"   Orders matched after grouping: {matched_grouped:,}")

        # Adjustment totals
        if "unavailable_items_adjustment" in final_df.columns:
            adj_mask = final_df["order_category"].isin(["Matched", "Matched (Grouped)"])
            adjustment_total = final_df.loc[adj_mask & order_mask, "unavailable_items_adjustment"].sum()
            if adjustment_total != 0:
                log(f"   Net adjustment value: £{adjustment_total:,.2f}")

        # Match quality breakdown
        if "variance_explanation" in final_df.columns:
            log("")
            log("Variance Analysis (Matched Orders):")
            variance_order = ["Exact Match", "Rounding", "Minor Variance", "Unexplained Variance"]
            for var_type in variance_order:
                if var_type in final_df["variance_explanation"].values:
                    count = (final_df["variance_explanation"] == var_type).sum()
                    log(f"   {var_type}: {count:,}")

        # Financial summary
        log("")
        log("Financial Summary:")

        order_rows = final_df[final_df["accounting_category"] == "Order Value & Commission"]
        matched_orders = order_rows[order_rows["order_category"].isin(["Matched", "Matched (Grouped)"])]

        if "order_value_gross" in final_df.columns:
            order_value_total = order_rows["order_value_gross"].sum()
            log(f"   Deliveroo Order Value (net): £{order_value_total:,.2f}")

        if "marketing_offer_discount" in final_df.columns:
            marketing_total = order_rows["marketing_offer_discount"].sum()
            if marketing_total != 0:
                log(f"   Marketing Discounts: £{marketing_total:,.2f}")

        if "gross_order_value" in final_df.columns:
            gross_total = order_rows["gross_order_value"].sum()
            log(f"   Gross Order Value: £{gross_total:,.2f}")

        if "unavailable_items_adjustment" in final_df.columns:
            adj_total = order_rows["unavailable_items_adjustment"].sum()
            if adj_total != 0:
                log(f"   Unavailable Items Adjustment: £{adj_total:,.2f}")

        if "net_sales_value" in final_df.columns:
            net_total = order_rows["net_sales_value"].sum()
            log(f"   Net Sales Value (comparable): £{net_total:,.2f}")

        if "dwh_post_promo_sales_inc_vat" in final_df.columns:
            dwh_product_total = matched_orders["dwh_post_promo_sales_inc_vat"].sum()
            log(f"   DWH Product Sales (matched): £{dwh_product_total:,.2f}")

        if "dwh_mp_bag_fee_inc_vat" in final_df.columns:
            dwh_bag_fee_total = matched_orders["dwh_mp_bag_fee_inc_vat"].sum()
            if dwh_bag_fee_total != 0:
                log(f"   DWH Bag Fees (matched): £{dwh_bag_fee_total:,.2f}")

        # 6) Save output
        log("")
        log("Step 5: Save Output")

        start_str = format_date(stmt_start, "%y.%m.%d")
        end_str = format_date(stmt_end_sunday, "%y.%m.%d")
        output_filename = f"{start_str} - {end_str} - Deliveroo Reconciliation.csv"
        output_path = output_folder / output_filename

        save_dataframe(final_df, output_path, backup_existing=False)

        log(f"Final rows: {len(final_df):,} | Columns: {len(final_df.columns)}")
        log(f"Saved -> {output_path.name}")
        log("Reconciliation complete!")

        return output_path

    except FileNotFoundError as e:
        log(f"Error: {e}")
        return None
    except Exception as e:
        log(f"Reconciliation failed: {e}")
        log_exception(e)
        return None


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
__all__ = [
    "load_dwh_deliveroo",
    "load_dr_combined",
    "aggregate_order_values",
    "match_deliveroo_orders",
    "calculate_variances",
    "run_dr_reconciliation",
]


# ====================================================================================================
# 99. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
def main() -> None:
    """
    Description:
        Self-test for DR02_data_reconciliation module.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Provides usage information when run directly.
        - For actual testing, call run_dr_reconciliation() with appropriate parameters.
    """
    logger.info("=" * 60)
    logger.info("DR02_data_reconciliation.py - Self Test")
    logger.info("=" * 60)
    logger.info("This module should be called via G10b controller or run_dr_reconciliation().")
    logger.info("For testing, provide dwh_folder, output_folder, and date parameters.")


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()