# ====================================================================================================
# DR_Audit.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo Reconciliation Audit Script
#
# Purpose:
#   - Comprehensive diagnostic tool for Deliveroo reconciliation output
#   - Analyzes value variances and identifies root causes
#   - Checks for collision risks in matching logic
#   - Looks up prior period DWH data for adjustments/refunds
#   - Validates match quality and flags issues
#
# Usage:
#   python DR_Audit.py
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-01-06
# Project:      Orders-to-Cash v1.0 - Diagnostic
# ====================================================================================================


# ====================================================================================================
# 1. IMPORTS & CONFIGURATION
# ====================================================================================================
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import Dict, List, Tuple, Optional


# ----------------------------------------------------------------------------------------------------
# CONFIGURATION - Update these paths as needed
# ----------------------------------------------------------------------------------------------------
CONFIG = {
    "reconciliation_file": Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output\25.12.01 - 26.01.04 - Deliveroo Reconciliation.csv"),
    "combined_file": Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output\25.12.01 - 26.01.04 - Deliveroo Combined.csv"),
    "dwh_folder": Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\03 DWH"),
    "variance_threshold_pct": 25.0,  # Flag matches with >25% variance
    "sample_size": 15,
}


# ====================================================================================================
# 2. DATA LOADING
# ====================================================================================================

def load_reconciliation(filepath: Path) -> pd.DataFrame:
    """Load the reconciliation CSV output from DR02."""
    print(f"\n{'='*80}")
    print("1. LOADING RECONCILIATION FILE")
    print(f"{'='*80}")
    print(f"   File: {filepath.name}")
    
    df = pd.read_csv(filepath, low_memory=False)
    print(f"   Total rows: {len(df):,}")
    print(f"   Total columns: {len(df.columns)}")
    
    return df


def load_combined(filepath: Path) -> pd.DataFrame:
    """Load the Deliveroo Combined CSV from DR01."""
    print(f"\n   Loading Combined file: {filepath.name}")
    
    df = pd.read_csv(filepath, low_memory=False)
    print(f"   Combined rows: {len(df):,}")
    
    return df


def load_dwh(folder: Path) -> pd.DataFrame:
    """Load all DWH CSV files (includes historical data)."""
    print(f"\n{'='*80}")
    print("2. LOADING DWH DATA (ALL PERIODS)")
    print(f"{'='*80}")
    
    csv_files = list(folder.glob("*.csv"))
    print(f"   Found {len(csv_files)} DWH files")
    
    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"   Warning: Failed to load {f.name}: {e}")
    
    if not dfs:
        raise FileNotFoundError(f"No valid DWH CSV files in {folder}")
    
    dwh_df = pd.concat(dfs, ignore_index=True)
    
    # Filter to Deliveroo only
    if "order_vendor" in dwh_df.columns:
        dwh_df = dwh_df[dwh_df["order_vendor"].str.lower() == "deliveroo"].copy()
    
    print(f"   Total Deliveroo DWH rows: {len(dwh_df):,}")
    
    # Show date range
    if "created_at_day" in dwh_df.columns:
        dates = pd.to_datetime(dwh_df["created_at_day"], errors="coerce")
        print(f"   Date range: {dates.min().date()} to {dates.max().date()}")
    
    return dwh_df


# ====================================================================================================
# 3. VARIANCE ANALYSIS
# ====================================================================================================

def analyse_variance_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze variance patterns in matched rows."""
    print(f"\n{'='*80}")
    print("3. VARIANCE ANALYSIS")
    print(f"{'='*80}")
    
    if "matched_amount" not in df.columns:
        print("   ERROR: matched_amount column not found")
        return pd.DataFrame()
    
    # Summary counts
    print(f"\n   --- Match Summary ---")
    for status in df["matched_amount"].unique():
        count = (df["matched_amount"] == status).sum()
        pct = count / len(df) * 100
        print(f"   {status}: {count:,} ({pct:.1f}%)")
    
    # Filter to variance rows
    variance_df = df[df["matched_amount"] == "Value Variance"].copy()
    exact_df = df[df["matched_amount"] == "Exact Match"].copy()
    
    if len(variance_df) == 0:
        print("\n   No variance rows to analyse.")
        return variance_df
    
    # Calculate variance stats
    if "amount_variance" in variance_df.columns and "dwh_post_promo_sales_inc_vat" in variance_df.columns:
        variance_df["abs_variance"] = variance_df["amount_variance"].abs()
        variance_df["abs_variance_pct"] = (
            variance_df["abs_variance"] / 
            variance_df["dwh_post_promo_sales_inc_vat"].replace(0, np.nan) * 100
        )
        
        print(f"\n   --- Variance Statistics ---")
        print(f"   Mean variance: £{variance_df['amount_variance'].mean():,.2f}")
        print(f"   Median variance: £{variance_df['amount_variance'].median():,.2f}")
        print(f"   Std deviation: £{variance_df['amount_variance'].std():,.2f}")
        
        print(f"\n   --- Variance % Distribution ---")
        bins = [(0, 1), (1, 5), (5, 20), (20, 50), (50, np.inf)]
        for low, high in bins:
            count = ((variance_df["abs_variance_pct"] >= low) & (variance_df["abs_variance_pct"] < high)).sum()
            pct = count / len(variance_df) * 100
            label = f"{low}-{high}%" if high != np.inf else f">{low}%"
            print(f"   {label:>10}: {count:>6,} ({pct:>5.1f}%)")
    
    # Date match analysis
    if "delivery_date" in variance_df.columns and "dwh_created_at_day" in variance_df.columns:
        exact_date = (variance_df["delivery_date"].astype(str) == variance_df["dwh_created_at_day"].astype(str)).sum()
        diff_date = len(variance_df) - exact_date
        print(f"\n   --- Date Match Analysis ---")
        print(f"   Exact date match: {exact_date:,}")
        print(f"   Different date (±1 day): {diff_date:,}")
    
    return variance_df


# ====================================================================================================
# 4. COLLISION RISK ANALYSIS
# ====================================================================================================

def analyse_collision_risk(recon_df: pd.DataFrame, dwh_df: pd.DataFrame, combined_df: pd.DataFrame) -> Dict:
    """Analyze collision risks in matching."""
    print(f"\n{'='*80}")
    print("4. COLLISION RISK ANALYSIS")
    print(f"{'='*80}")
    
    results = {
        "dwh_duplicates": 0,
        "dr_duplicates": 0,
        "zero_order_numbers": 0,
    }
    
    # --- DWH Duplicates ---
    print(f"\n   --- DWH Duplicate Keys ---")
    dwh_df["match_key"] = (
        dwh_df["mp_order_id"].astype(str) + "|" + 
        dwh_df["location_name"].astype(str) + "|" + 
        dwh_df["created_at_day"].astype(str)
    )
    dwh_dups = dwh_df.groupby("match_key").size().reset_index(name="count")
    dwh_dups = dwh_dups[dwh_dups["count"] > 1]
    results["dwh_duplicates"] = len(dwh_dups)
    print(f"   Duplicate (last4 + mfc + date) in DWH: {len(dwh_dups):,}")
    
    # --- Deliveroo Duplicates ---
    print(f"\n   --- Deliveroo Duplicate Keys ---")
    if "order_last4" in combined_df.columns and "mfc_name" in combined_df.columns:
        combined_df["match_key"] = (
            combined_df["order_last4"].astype(str) + "|" + 
            combined_df["mfc_name"].astype(str) + "|" + 
            combined_df["delivery_date"].astype(str)
        )
        dr_dups = combined_df.groupby("match_key").size().reset_index(name="count")
        dr_dups = dr_dups[dr_dups["count"] > 1]
        results["dr_duplicates"] = len(dr_dups)
        print(f"   Duplicate keys in Deliveroo data: {len(dr_dups):,}")
    
    # --- Zero Order Numbers ---
    print(f"\n   --- Zero/Missing Order Numbers ---")
    zero_orders = recon_df[recon_df["order_number"] == 0]
    results["zero_order_numbers"] = len(zero_orders)
    print(f"   Rows with order_number = 0: {len(zero_orders):,}")
    
    if len(zero_orders) > 0:
        print(f"\n   Breakdown by accounting_category:")
        for cat, count in zero_orders["accounting_category"].value_counts().items():
            print(f"      {cat}: {count:,}")
    
    return results


# ====================================================================================================
# 5. PRIOR PERIOD LOOKUP
# ====================================================================================================

def lookup_prior_period_orders(
    variance_df: pd.DataFrame, 
    dwh_df: pd.DataFrame,
    threshold_pct: float = 25.0
) -> pd.DataFrame:
    """
    For high-variance matches, search DWH across all periods to find the correct order.
    This handles cases where adjustments appear in current period but order was from prior month.
    """
    print(f"\n{'='*80}")
    print("5. PRIOR PERIOD ORDER LOOKUP")
    print(f"{'='*80}")
    
    if len(variance_df) == 0:
        print("   No variance rows to check.")
        return pd.DataFrame()
    
    # Filter to high-variance rows (likely wrong matches or prior period)
    if "abs_variance_pct" not in variance_df.columns:
        variance_df["abs_variance_pct"] = (
            variance_df["amount_variance"].abs() / 
            variance_df["dwh_post_promo_sales_inc_vat"].replace(0, np.nan) * 100
        )
    
    high_variance = variance_df[variance_df["abs_variance_pct"] > threshold_pct].copy()
    print(f"   High variance rows (>{threshold_pct}%): {len(high_variance):,}")
    
    if len(high_variance) == 0:
        print("   No high-variance rows to investigate.")
        return pd.DataFrame()
    
    # Calculate expected value for matching
    high_variance["expected_value"] = (
        high_variance["order_value_gross"].fillna(0) + 
        high_variance["marketing_offer_discount"].fillna(0)
    )
    
    # Build DWH lookup by (mp_order_id, location_name) -> all matching rows
    print(f"\n   Building DWH lookup index...")
    dwh_lookup: Dict[Tuple[str, str], List[Dict]] = {}
    
    for _, row in dwh_df.iterrows():
        mp_id = str(int(row["mp_order_id"])) if pd.notna(row["mp_order_id"]) else ""
        loc = str(row.get("location_name", ""))
        
        if mp_id and loc:
            key = (mp_id, loc)
            if key not in dwh_lookup:
                dwh_lookup[key] = []
            dwh_lookup[key].append({
                "gp_order_id": row.get("gp_order_id"),
                "created_at_day": row.get("created_at_day"),
                "post_promo_sales_inc_vat": row.get("post_promo_sales_inc_vat", 0),
            })
    
    print(f"   DWH lookup keys: {len(dwh_lookup):,}")
    
    # Search for better matches
    results = []
    found_prior = 0
    not_found = 0
    
    for idx, row in high_variance.iterrows():
        order_last4 = str(row.get("order_last4", "")).strip()
        mfc_name = str(row.get("mfc_name", "")).strip()
        expected_val = row["expected_value"]
        current_dwh_date = row.get("dwh_created_at_day", "")
        
        key = (order_last4, mfc_name)
        
        result = {
            "order_number": row.get("order_number"),
            "order_last4": order_last4,
            "mfc_name": mfc_name,
            "delivery_date": row.get("delivery_date"),
            "expected_value": expected_val,
            "current_dwh_date": current_dwh_date,
            "current_dwh_value": row.get("dwh_post_promo_sales_inc_vat"),
            "variance_pct": row.get("abs_variance_pct"),
            "accounting_category": row.get("accounting_category"),
            "note": row.get("note", "")[:100] if pd.notna(row.get("note")) else "",
        }
        
        if key in dwh_lookup:
            # Find the DWH row with closest value match
            candidates = dwh_lookup[key]
            best_match = None
            best_diff = float("inf")
            
            for cand in candidates:
                diff = abs(cand["post_promo_sales_inc_vat"] - expected_val)
                if diff < best_diff:
                    best_diff = diff
                    best_match = cand
            
            if best_match:
                result["best_match_date"] = best_match["created_at_day"]
                result["best_match_value"] = best_match["post_promo_sales_inc_vat"]
                result["best_match_diff"] = best_diff
                result["best_match_gp_id"] = best_match["gp_order_id"]
                
                # Check if best match is from a different date (prior period)
                if str(best_match["created_at_day"]) != str(current_dwh_date):
                    result["status"] = "PRIOR_PERIOD_FOUND"
                    found_prior += 1
                elif best_diff < expected_val * 0.05:  # Within 5%
                    result["status"] = "BETTER_MATCH_SAME_DATE"
                else:
                    result["status"] = "NO_GOOD_MATCH"
                    not_found += 1
            else:
                result["status"] = "NO_DWH_RECORD"
                not_found += 1
        else:
            result["status"] = "NO_DWH_RECORD"
            not_found += 1
        
        results.append(result)
    
    results_df = pd.DataFrame(results)
    
    print(f"\n   --- Prior Period Lookup Results ---")
    if "status" in results_df.columns:
        for status, count in results_df["status"].value_counts().items():
            print(f"   {status}: {count:,}")
    
    return results_df


# ====================================================================================================
# 6. SAMPLE COMPARISON OUTPUT
# ====================================================================================================

def show_sample_comparisons(variance_df: pd.DataFrame, n_samples: int = 15) -> None:
    """Show side-by-side comparison of sample variance rows."""
    print(f"\n{'='*80}")
    print(f"6. SAMPLE VARIANCE COMPARISONS (n={n_samples})")
    print(f"{'='*80}")
    
    if len(variance_df) == 0:
        print("   No variance rows to sample.")
        return
    
    sample = variance_df.sample(n=min(n_samples, len(variance_df)), random_state=42)
    
    for idx, (_, row) in enumerate(sample.iterrows(), 1):
        order_num = row.get("order_number", "N/A")
        last4 = row.get("order_last4", "N/A")
        mfc = row.get("mfc_name", "N/A")
        dr_date = row.get("delivery_date", "N/A")
        dwh_date = row.get("dwh_created_at_day", "N/A")
        
        dr_val = row.get("order_value_gross", 0) or 0
        discount = row.get("marketing_offer_discount", 0) or 0
        expected = dr_val + discount
        dwh_val = row.get("dwh_post_promo_sales_inc_vat", 0) or 0
        variance = expected - dwh_val
        var_pct = (variance / dwh_val * 100) if dwh_val else 0
        
        category = row.get("accounting_category", "N/A")
        note = str(row.get("note", ""))[:60] if pd.notna(row.get("note")) else ""
        
        print(f"\n   [{idx}] Order: {order_num} | Last4: {last4} | MFC: {mfc}")
        print(f"       DR Date: {dr_date} | DWH Date: {dwh_date}")
        print(f"       Category: {category}")
        print(f"       DR order_value_gross:     £{dr_val:>10.2f}")
        print(f"       DR marketing_discount:    £{discount:>10.2f}")
        print(f"       DR Expected Total:        £{expected:>10.2f}")
        print(f"       DWH post_promo_sales:     £{dwh_val:>10.2f}")
        print(f"       VARIANCE:                 £{variance:>10.2f} ({var_pct:.1f}%)")
        if note:
            print(f"       Note: {note}...")


# ====================================================================================================
# 7. ADJUSTMENT ANALYSIS
# ====================================================================================================

def analyse_adjustments(recon_df: pd.DataFrame) -> None:
    """Analyze adjustment patterns - these reference prior orders."""
    print(f"\n{'='*80}")
    print("7. ADJUSTMENT ANALYSIS")
    print(f"{'='*80}")
    
    # Identify adjustment rows
    adjustment_categories = ["Additional Fees", "Additional Payments", "Exclude", "Uncategorised"]
    adjustments = recon_df[recon_df["accounting_category"].isin(adjustment_categories)].copy()
    
    print(f"\n   Total adjustment rows: {len(adjustments):,}")
    
    print(f"\n   --- By Category ---")
    for cat in adjustment_categories:
        count = (adjustments["accounting_category"] == cat).sum()
        if count > 0:
            total = adjustments[adjustments["accounting_category"] == cat]["total_payable"].sum()
            print(f"   {cat}: {count:,} rows | £{total:,.2f}")
    
    # Check which have order numbers (can be linked to original orders)
    has_order = adjustments[adjustments["order_number"] != 0]
    no_order = adjustments[adjustments["order_number"] == 0]
    
    print(f"\n   --- Order Number Availability ---")
    print(f"   With order_number: {len(has_order):,} (can link to original order)")
    print(f"   Without order_number: {len(no_order):,} (standalone adjustments)")
    
    # Sample adjustments with order numbers
    if len(has_order) > 0:
        print(f"\n   --- Sample Adjustments with Order Numbers ---")
        sample = has_order.head(5)
        for _, row in sample.iterrows():
            print(f"   Order: {row['order_number']} | {row['accounting_category']} | £{row['total_payable']:.2f}")


# ====================================================================================================
# 8. RECOMMENDATIONS
# ====================================================================================================

def generate_recommendations(
    recon_df: pd.DataFrame, 
    variance_df: pd.DataFrame,
    prior_lookup_df: pd.DataFrame,
    collision_stats: Dict
) -> None:
    """Generate actionable recommendations based on analysis."""
    print(f"\n{'='*80}")
    print("8. RECOMMENDATIONS")
    print(f"{'='*80}")
    
    total_matched = (recon_df["order_category"] == "Matched").sum()
    total_deliveries = (recon_df["accounting_category"] == "Order Value & Commission").sum()
    match_rate = total_matched / total_deliveries * 100 if total_deliveries else 0
    
    exact_match = (recon_df["matched_amount"] == "Exact Match").sum()
    exact_rate = exact_match / total_matched * 100 if total_matched else 0
    
    print(f"\n   --- Current State ---")
    print(f"   Match rate: {match_rate:.1f}% ({total_matched:,} / {total_deliveries:,} deliveries)")
    print(f"   Exact match rate: {exact_rate:.1f}% ({exact_match:,} / {total_matched:,} matched)")
    print(f"   Value variance rows: {len(variance_df):,}")
    
    print(f"\n   --- Issues Identified ---")
    
    issues = []
    
    # High variance due to prior period
    if len(prior_lookup_df) > 0 and "status" in prior_lookup_df.columns:
        prior_period = (prior_lookup_df["status"] == "PRIOR_PERIOD_FOUND").sum()
        if prior_period > 0:
            issues.append(f"   • {prior_period:,} orders matched to wrong DWH record (original order in prior period)")
    
    # DWH duplicates
    if collision_stats.get("dwh_duplicates", 0) > 0:
        issues.append(f"   • {collision_stats['dwh_duplicates']:,} duplicate keys in DWH causing potential mis-matches")
    
    # Missing DWH records
    if len(prior_lookup_df) > 0 and "status" in prior_lookup_df.columns:
        no_record = (prior_lookup_df["status"] == "NO_DWH_RECORD").sum()
        if no_record > 0:
            issues.append(f"   • {no_record:,} Deliveroo orders have no matching DWH record at all")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("   No major issues identified.")
    
    print(f"\n   --- Suggested Actions ---")
    print("   1. Adjustments (refunds, fees) should inherit match from original order, not re-match")
    print("   2. Add value-based validation: reject matches where variance >25%")
    print("   3. For unmatched adjustments, search historical DWH by order_number")
    print("   4. Flag 'Matched with Variance' separately from 'Exact Match' in reports")


# ====================================================================================================
# 9. MAIN EXECUTION
# ====================================================================================================

def main() -> None:
    """Main audit execution."""
    print("\n" + "=" * 80)
    print("DELIVEROO RECONCILIATION AUDIT")
    print("=" * 80)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    recon_df = load_reconciliation(CONFIG["reconciliation_file"])
    combined_df = load_combined(CONFIG["combined_file"])
    dwh_df = load_dwh(CONFIG["dwh_folder"])
    
    # Run analyses
    variance_df = analyse_variance_summary(recon_df)
    collision_stats = analyse_collision_risk(recon_df, dwh_df, combined_df)
    
    prior_lookup_df = pd.DataFrame()
    if len(variance_df) > 0:
        prior_lookup_df = lookup_prior_period_orders(
            variance_df, 
            dwh_df, 
            threshold_pct=CONFIG["variance_threshold_pct"]
        )
    
    show_sample_comparisons(variance_df, n_samples=CONFIG["sample_size"])
    analyse_adjustments(recon_df)
    generate_recommendations(recon_df, variance_df, prior_lookup_df, collision_stats)
    
    print(f"\n{'='*80}")
    print("AUDIT COMPLETE")
    print(f"{'='*80}\n")
    
    # Return dataframes for interactive use
    return {
        "recon_df": recon_df,
        "variance_df": variance_df,
        "prior_lookup_df": prior_lookup_df,
        "dwh_df": dwh_df,
    }


if __name__ == "__main__":
    results = main()