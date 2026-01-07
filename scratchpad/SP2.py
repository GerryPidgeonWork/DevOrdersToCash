import pandas as pd

# Add to SP1.py or run ad-hoc
df = pd.read_csv(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output\25.12.01 - 26.01.04 - Deliveroo Reconciliation.csv", low_memory=False)

# Filter to matched deliveries with variance
variance_rows = df[(df["order_category"] == "Matched") & (df["matched_amount"] == "Value Variance")]

print(f"Total variance rows: {len(variance_rows)}")

# Variance magnitude breakdown
variance_rows["abs_variance"] = variance_rows["amount_variance"].abs()
variance_rows["abs_variance_pct"] = (variance_rows["abs_variance"] / variance_rows["dwh_post_promo_sales_inc_vat"] * 100)

print(f"\nVariance magnitude breakdown:")
print(f"  < 1%:    {(variance_rows['abs_variance_pct'] < 1).sum()}")
print(f"  1-5%:    {((variance_rows['abs_variance_pct'] >= 1) & (variance_rows['abs_variance_pct'] < 5)).sum()}")
print(f"  5-20%:   {((variance_rows['abs_variance_pct'] >= 5) & (variance_rows['abs_variance_pct'] < 20)).sum()}")
print(f"  20-50%:  {((variance_rows['abs_variance_pct'] >= 20) & (variance_rows['abs_variance_pct'] < 50)).sum()}")
print(f"  > 50%:   {(variance_rows['abs_variance_pct'] >= 50).sum()}")

# Check if dates match exactly or within ±1 day
print(f"\nDate match analysis:")
print(f"  Exact date match: {(variance_rows['delivery_date'] == variance_rows['dwh_created_at_day']).sum()}")
print(f"  Different date:   {(variance_rows['delivery_date'] != variance_rows['dwh_created_at_day']).sum()}")

# Sample high-variance rows
high_var = variance_rows[variance_rows["abs_variance_pct"] > 50].head(5)
print(f"\nSample high-variance rows (>50%):")
print(high_var[["order_number", "mfc_name", "delivery_date", "dwh_created_at_day", "order_value_gross", "marketing_offer_discount", "dwh_post_promo_sales_inc_vat", "amount_variance"]].to_string())