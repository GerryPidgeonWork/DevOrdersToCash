import pandas as pd

# Check if multiple Deliveroo orders share the same key
dr_file = r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output\25.12.01 - 26.01.04 - Deliveroo Reconciliation.csv"
dr_df = pd.read_csv(dr_file, low_memory=False)

# Create match key
dr_df["order_last4"] = dr_df["order_number"].astype(str).str[-4:]
dr_df["delivery_date"] = pd.to_datetime(dr_df["delivery_datetime_utc"]).dt.date.astype(str)
dr_df["match_key"] = dr_df["order_last4"] + "|" + dr_df["mfc_name"] + "|" + dr_df["delivery_date"]

# Check duplicates
dr_duplicates = dr_df.groupby("match_key").size().reset_index(name="count")
dr_duplicates = dr_duplicates[dr_duplicates["count"] > 1]

print(f"Duplicate keys in Deliveroo data: {len(dr_duplicates)}")

# Check specific problematic order
print(f"\nLooking up order 50405289095:")
print(dr_df[dr_df["order_number"] == 50405289095][["order_number", "order_last4", "mfc_name", "delivery_date", "order_value_gross", "marketing_offer_discount"]].to_string())

# Check if there are other 9095 orders at same location/date
print(f"\nAll 9095 orders at LHR_London_1291 on 2025-12-01:")
mask = (dr_df["order_last4"] == "9095") & (dr_df["mfc_name"] == "LHR_London_1291") & (dr_df["delivery_date"] == "2025-12-01")
print(dr_df[mask][["order_number", "order_value_gross", "marketing_offer_discount"]].to_string())

# Check what's in those duplicate rows
print("Full details of order 50405289095:")
cols = ["order_number", "accounting_category", "activity", "order_value_gross", "commission_net", "adjustment_net", "total_payable", "note"]
print(dr_df[dr_df["order_number"] == 50405289095][[c for c in cols if c in dr_df.columns]].to_string())

# Check the overall pattern of duplicates
print("\n\nAccounting category breakdown for duplicate orders:")
dup_keys = dr_duplicates["match_key"].tolist()
dup_rows = dr_df[dr_df["match_key"].isin(dup_keys)]
print(dup_rows["accounting_category"].value_counts())