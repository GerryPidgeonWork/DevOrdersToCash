import pandas as pd
from pathlib import Path

# Load DWH data
dwh_files = list(Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\03 DWH").glob("*.csv"))
dwh_df = pd.concat([pd.read_csv(f, low_memory=False) for f in dwh_files])

# Load Deliveroo data
dr_df = pd.read_csv(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output\25.12.01 - 26.01.04 - Deliveroo Combined.csv", low_memory=False)

# Check timestamp for the problematic Deliveroo order
print("Deliveroo order 50405289095 details:")
dr_order = dr_df[dr_df["order_number"] == 50405289095]
print(dr_order[["order_number", "delivery_datetime_utc", "mfc_name", "order_value_gross", "marketing_offer_discount"]].head(1).to_string())

# Expected value to match
expected_value = 44.1 + 44.4  # = 88.5
print(f"\nExpected DWH post_promo_sales_inc_vat: ~£{expected_value}")

# Search DWH for any order at this MFC with value close to £88.50
london_1291 = dwh_df[dwh_df["location_name"] == "LHR_London_1291"]
close_value = london_1291[
    (london_1291["post_promo_sales_inc_vat"] > 85) & 
    (london_1291["post_promo_sales_inc_vat"] < 92)
]
print(f"\nDWH orders at LHR_London_1291 with value £85-92:")
print(close_value[["gp_order_id", "mp_order_id", "created_at_day", "created_at_timestamp", "post_promo_sales_inc_vat"]].head(20).to_string())

# Check if any have mp_order_id = 9095
print(f"\nOf those, with mp_order_id ending in 9095:")
close_value_9095 = close_value[close_value["mp_order_id"] == 9095]
print(close_value_9095[["gp_order_id", "mp_order_id", "created_at_day", "post_promo_sales_inc_vat"]].to_string())

# Also search all DWH for mp_order_id = 9095 to see all instances
print(f"\nAll DWH rows with mp_order_id = 9095:")
all_9095 = dwh_df[dwh_df["mp_order_id"] == 9095]
print(all_9095[["gp_order_id", "mp_order_id", "location_name", "created_at_day", "post_promo_sales_inc_vat"]].to_string())