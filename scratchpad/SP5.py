# ====================================================================================================
# SP1.py
# ----------------------------------------------------------------------------------------------------
# Support Script 1 - Deliveroo Reconciliation Diagnostic
#
# Purpose:
#   - Investigate the 99% "Value Variance" issue in DR02 reconciliation output.
#   - Sample and display side-by-side comparison of Deliveroo vs DWH values.
#   - Identify systematic patterns causing variance.
#   - Check for potential last-4-digit collision issues.
#
# Usage:
#   python SP1.py <reconciliation_csv_path>
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-01-06
# Project:      Orders-to-Cash v1.0 - Diagnostic
# ====================================================================================================


# ====================================================================================================
# 1. IMPORTS
# ====================================================================================================
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import date


# ====================================================================================================
# 2. DIAGNOSTIC FUNCTIONS
# ====================================================================================================

def load_reconciliation(filepath: Path) -> pd.DataFrame:
    """Load the reconciliation CSV output from DR02."""
    print(f"\n{'='*70}")
    print("LOADING RECONCILIATION FILE")
    print(f"{'='*70}")
    print(f"File: {filepath.name}")
    
    df = pd.read_csv(filepath, low_memory=False)
    print(f"Total rows: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    
    return df


def analyse_value_variance(df: pd.DataFrame) -> None:
    """Analyse the Value Variance rows to identify patterns."""
    print(f"\n{'='*70}")
    print("VALUE VARIANCE ANALYSIS")
    print(f"{'='*70}")
    
    # Filter to matched rows with variance
    if "matched_amount" not in df.columns:
        print("ERROR: matched_amount column not found")
        return
    
    variance_df = df[df["matched_amount"] == "Value Variance"].copy()
    exact_df = df[df["matched_amount"] == "Exact Match"].copy()
    
    print(f"\nValue Variance rows: {len(variance_df):,}")
    print(f"Exact Match rows: {len(exact_df):,}")
    
    if len(variance_df) == 0:
        print("No variance rows to analyse.")
        return
    
    # Key columns for comparison
    dr_col = "order_value_gross"
    dwh_col = "dwh_total_payment_with_tips_inc_vat"
    
    if dr_col not in variance_df.columns or dwh_col not in variance_df.columns:
        print(f"ERROR: Missing columns. Available: {list(variance_df.columns)[:20]}...")
        return
    
    # Calculate variance statistics
    variance_df["calc_variance"] = variance_df[dr_col] - variance_df[dwh_col]
    variance_df["variance_pct"] = (variance_df["calc_variance"] / variance_df[dwh_col] * 100).round(2)
    
    print(f"\n--- Variance Statistics ---")
    print(f"Mean variance: £{variance_df['calc_variance'].mean():,.2f}")
    print(f"Median variance: £{variance_df['calc_variance'].median():,.2f}")
    print(f"Std deviation: £{variance_df['calc_variance'].std():,.2f}")
    print(f"Min variance: £{variance_df['calc_variance'].min():,.2f}")
    print(f"Max variance: £{variance_df['calc_variance'].max():,.2f}")
    
    print(f"\n--- Variance % Statistics ---")
    print(f"Mean variance %: {variance_df['variance_pct'].mean():.2f}%")
    print(f"Median variance %: {variance_df['variance_pct'].median():.2f}%")
    
    # Distribution of variance percentages
    print(f"\n--- Variance % Distribution ---")
    bins = [(-np.inf, -10), (-10, -5), (-5, -1), (-1, 1), (1, 5), (5, 10), (10, 20), (20, 50), (50, np.inf)]
    for low, high in bins:
        count = ((variance_df["variance_pct"] > low) & (variance_df["variance_pct"] <= high)).sum()
        pct = count / len(variance_df) * 100
        print(f"   {low:>6} to {high:<6}: {count:>6,} ({pct:>5.1f}%)")


def show_sample_comparisons(df: pd.DataFrame, n_samples: int = 15) -> None:
    """Show side-by-side comparison of sample variance rows."""
    print(f"\n{'='*70}")
    print(f"SAMPLE COMPARISONS (n={n_samples})")
    print(f"{'='*70}")
    
    variance_df = df[df["matched_amount"] == "Value Variance"].copy()
    
    if len(variance_df) == 0:
        print("No variance rows to sample.")
        return
    
    # Sample rows
    sample = variance_df.sample(n=min(n_samples, len(variance_df)), random_state=42)
    
    # Identify available columns
    dr_cols = ["order_number", "order_last4", "mfc_name", "delivery_date", "order_value_gross"]
    dwh_cols = ["dwh_mp_order_id", "dwh_location_name", "dwh_created_at_day", 
                "dwh_total_payment_with_tips_inc_vat", "dwh_total_payment_inc_vat",
                "dwh_post_promo_sales_inc_vat", "dwh_delivery_fee_inc_vat", 
                "dwh_priority_fee_inc_vat", "dwh_small_order_fee_inc_vat",
                "dwh_mp_bag_fee_inc_vat", "dwh_tips_amount"]
    
    # Filter to available columns
    dr_cols = [c for c in dr_cols if c in sample.columns]
    dwh_cols = [c for c in dwh_cols if c in sample.columns]
    
    print(f"\n--- Deliveroo Columns Available ---")
    print(f"   {dr_cols}")
    print(f"\n--- DWH Columns Available ---")
    print(f"   {dwh_cols}")
    
    print(f"\n--- Side-by-Side Sample ---")
    print("-" * 120)
    
    for idx, (_, row) in enumerate(sample.iterrows(), 1):
        dr_val = row.get("order_value_gross", 0)
        dwh_val = row.get("dwh_total_payment_with_tips_inc_vat", 0)
        variance = dr_val - dwh_val
        
        print(f"\n[{idx}] Order: {row.get('order_number', 'N/A')} | Last4: {row.get('order_last4', 'N/A')} | MFC: {row.get('mfc_name', 'N/A')}")
        print(f"    Deliveroo order_value_gross:         £{dr_val:>10.2f}")
        print(f"    DWH total_payment_with_tips_inc_vat: £{dwh_val:>10.2f}")
        print(f"    VARIANCE:                            £{variance:>10.2f} ({variance/dwh_val*100 if dwh_val else 0:.1f}%)")
        
        # Show DWH component breakdown if available
        components = []
        for col in ["dwh_post_promo_sales_inc_vat", "dwh_delivery_fee_inc_vat", 
                    "dwh_priority_fee_inc_vat", "dwh_small_order_fee_inc_vat", 
                    "dwh_mp_bag_fee_inc_vat", "dwh_tips_amount"]:
            if col in row and pd.notna(row[col]) and row[col] != 0:
                short_name = col.replace("dwh_", "").replace("_inc_vat", "").replace("_", " ")
                components.append(f"{short_name}: £{row[col]:.2f}")
        
        if components:
            print(f"    DWH Components: {' | '.join(components)}")
        
        # Calculate what DWH total SHOULD be from components
        calc_total = sum([
            row.get("dwh_post_promo_sales_inc_vat", 0) or 0,
            row.get("dwh_delivery_fee_inc_vat", 0) or 0,
            row.get("dwh_priority_fee_inc_vat", 0) or 0,
            row.get("dwh_small_order_fee_inc_vat", 0) or 0,
            row.get("dwh_mp_bag_fee_inc_vat", 0) or 0,
            row.get("dwh_tips_amount", 0) or 0,
        ])
        if calc_total > 0:
            print(f"    DWH Calculated Total (components):   £{calc_total:>10.2f}")


def check_collision_risk(df: pd.DataFrame) -> None:
    """Check for potential last-4-digit collision issues."""
    print(f"\n{'='*70}")
    print("COLLISION RISK ANALYSIS")
    print(f"{'='*70}")
    
    if "order_last4" not in df.columns or "mfc_name" not in df.columns:
        print("Required columns not found.")
        return
    
    # Check how many unique full order numbers share the same last4+mfc combo
    if "order_number" in df.columns:
        combo_df = df[["order_number", "order_last4", "mfc_name", "delivery_date"]].copy()
        combo_df["combo_key"] = combo_df["order_last4"].astype(str) + "|" + combo_df["mfc_name"].astype(str) + "|" + combo_df["delivery_date"].astype(str)
        
        # Count unique order_numbers per combo_key
        collision_check = combo_df.groupby("combo_key")["order_number"].nunique().reset_index()
        collision_check.columns = ["combo_key", "unique_orders"]
        
        collisions = collision_check[collision_check["unique_orders"] > 1]
        
        print(f"\nTotal unique (last4 + mfc + date) combinations: {len(collision_check):,}")
        print(f"Combinations with multiple different order numbers: {len(collisions):,}")
        
        if len(collisions) > 0:
            print(f"\n--- Sample Collisions (up to 10) ---")
            for _, row in collisions.head(10).iterrows():
                key = row["combo_key"]
                matching = combo_df[combo_df["combo_key"] == key]["order_number"].unique()
                print(f"   Key: {key}")
                print(f"   Orders: {list(matching)[:5]}{'...' if len(matching) > 5 else ''}")


def analyse_field_definitions(df: pd.DataFrame) -> None:
    """Analyse what fields might be included/excluded."""
    print(f"\n{'='*70}")
    print("FIELD DEFINITION ANALYSIS")
    print(f"{'='*70}")
    
    matched_df = df[df["order_category"] == "Matched"].copy()
    
    if len(matched_df) == 0:
        print("No matched rows to analyse.")
        return
    
    # Check if commission is the difference
    if "commission_gross" in matched_df.columns:
        matched_df["dr_minus_commission"] = matched_df["order_value_gross"] - matched_df["commission_gross"]
        matched_df["diff_from_dwh"] = matched_df["dr_minus_commission"] - matched_df["dwh_total_payment_with_tips_inc_vat"]
        
        close_after_commission = (matched_df["diff_from_dwh"].abs() < 0.02).sum()
        print(f"\nOrders matching DWH after subtracting commission: {close_after_commission:,} ({close_after_commission/len(matched_df)*100:.1f}%)")
    
    # Check relationship between DR and DWH values
    print(f"\n--- Correlation Analysis ---")
    
    dr_val = matched_df["order_value_gross"]
    dwh_val = matched_df["dwh_total_payment_with_tips_inc_vat"]
    
    if dwh_val.sum() > 0:
        ratio = dr_val.sum() / dwh_val.sum()
        print(f"Total DR / Total DWH ratio: {ratio:.4f}")
        print(f"This suggests DR values are ~{(ratio-1)*100:.1f}% {'higher' if ratio > 1 else 'lower'} than DWH")
        
        # Per-row ratio analysis
        matched_df["row_ratio"] = dr_val / dwh_val.replace(0, np.nan)
        print(f"\nPer-row ratio stats:")
        print(f"   Mean: {matched_df['row_ratio'].mean():.4f}")
        print(f"   Median: {matched_df['row_ratio'].median():.4f}")
        print(f"   Mode (rounded to 2dp): {matched_df['row_ratio'].round(2).mode().values[0] if len(matched_df['row_ratio'].round(2).mode()) > 0 else 'N/A'}")


def check_dwh_field_availability(df: pd.DataFrame) -> None:
    """Check which DWH fields are actually populated."""
    print(f"\n{'='*70}")
    print("DWH FIELD AVAILABILITY")
    print(f"{'='*70}")
    
    matched_df = df[df["order_category"] == "Matched"].copy()
    dwh_cols = [c for c in matched_df.columns if c.startswith("dwh_")]
    
    print(f"\nDWH columns found: {len(dwh_cols)}")
    print(f"\n--- Population Rates (matched rows) ---")
    
    for col in sorted(dwh_cols):
        non_null = matched_df[col].notna().sum()
        non_zero = (matched_df[col] != 0).sum() if matched_df[col].dtype in ['int64', 'float64'] else non_null
        pct = non_null / len(matched_df) * 100
        
        # Show sum for numeric columns
        if matched_df[col].dtype in ['int64', 'float64']:
            total = matched_df[col].sum()
            print(f"   {col:<45} {non_null:>6,} ({pct:>5.1f}%) | Sum: £{total:>12,.2f}")
        else:
            print(f"   {col:<45} {non_null:>6,} ({pct:>5.1f}%)")


def generate_recommendations(df: pd.DataFrame) -> None:
    """Generate recommendations based on analysis."""
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}")
    
    matched_df = df[df["order_category"] == "Matched"].copy()
    
    if len(matched_df) == 0:
        print("Insufficient data for recommendations.")
        return
    
    dr_total = matched_df["order_value_gross"].sum()
    dwh_total = matched_df["dwh_total_payment_with_tips_inc_vat"].sum()
    
    print(f"\n1. FIELD MISMATCH CHECK:")
    print(f"   - Deliveroo 'order_value_gross' total: £{dr_total:,.2f}")
    print(f"   - DWH 'total_payment_with_tips_inc_vat' total: £{dwh_total:,.2f}")
    print(f"   - Difference: £{dr_total - dwh_total:,.2f} ({(dr_total/dwh_total-1)*100:.1f}%)")
    
    # Check if commission explains it
    if "commission_gross" in matched_df.columns:
        commission_total = matched_df["commission_gross"].sum()
        print(f"\n   - Total commission (gross): £{commission_total:,.2f}")
        print(f"   - DR minus commission: £{dr_total - commission_total:,.2f}")
        
        if abs((dr_total - commission_total) - dwh_total) < abs(dr_total - dwh_total) * 0.1:
            print(f"\n   ⚠️  LIKELY CAUSE: 'order_value_gross' includes commission that DWH excludes!")
            print(f"       Consider comparing 'order_value_gross - commission_gross' against DWH.")
    
    print(f"\n2. NEXT STEPS:")
    print(f"   a) Verify field definitions with DWH documentation")
    print(f"   b) Check if 'dwh_post_promo_sales_inc_vat' is the correct comparison field")
    print(f"   c) Confirm whether DR 'order_value_gross' includes commission")
    print(f"   d) Review a few orders manually in source systems")


# ====================================================================================================
# 3. MAIN EXECUTION
# ====================================================================================================

def main(filepath: str | None = None) -> None:
    """Main diagnostic execution."""
    print("\n" + "=" * 70)
    print("SP1.py - DELIVEROO RECONCILIATION DIAGNOSTIC")
    print("=" * 70)
    
    # Get filepath from argument or prompt
    if filepath is None:
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
        else:
            print("\nUsage: python SP1.py <reconciliation_csv_path>")
            print("\nPlease provide path to DR02 reconciliation output CSV.")
            return
    
    csv_path = Path(filepath)
    
    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return
    
    # Run diagnostics
    df = load_reconciliation(csv_path)
    analyse_value_variance(df)
    show_sample_comparisons(df, n_samples=15)
    check_collision_risk(df)
    analyse_field_definitions(df)
    check_dwh_field_availability(df)
    generate_recommendations(df)
    
    print(f"\n{'='*70}")
    print("DIAGNOSTIC COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()