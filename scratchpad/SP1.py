"""
JE01 Debug Trace Script
-----------------------
Diagnostic tool to trace what extract_descriptions() and extract_amounts() 
return for a specific PDF, and how they're paired in build_refund_dataframe().

Usage:
    python je_debug_trace.py "path/to/pdf.pdf"
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# PDF extraction libraries
import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text

import pandas as pd


# ============================================================================
# FUNCTIONS (copied from JE01_parse_pdfs.py for standalone use)
# ============================================================================

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text using pdfminer."""
    return pdfminer_extract_text(str(pdf_path))


def get_segment_text(pdf_path: Path) -> str:
    """Extract the 'Commission to Just Eat' section from a PDF."""
    txt = extract_pdf_text(pdf_path)
    start = txt.find("Commission to Just Eat")
    if start == -1:
        return ""
    
    end = txt.find("Your Just Eat account statement", start)
    if end == -1:
        end = txt.find("You don't need to do anything", start)
    if end == -1:
        end = txt.find("Subtotal", start)
    if end == -1:
        return ""
    
    return txt[start:end]


def extract_descriptions(segment_text: str) -> List[str]:
    """Extract description lines from the commission/refund segment."""
    if not segment_text:
        return []

    lines = [re.sub(r"\s+", " ", ln).strip() for ln in segment_text.splitlines()]
    lines = [ln for ln in lines if ln]

    money_re = re.compile(r"[–\-]?\s*£\s*[0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2}")
    lines = [money_re.sub("", ln).strip() for ln in lines if not money_re.fullmatch(ln)]

    merged = []
    for ln in lines:
        if not merged:
            merged.append(ln)
            continue
        # Start new entry if:
        # - Line begins with uppercase, OR
        # - Line begins with digit AND has '%' early (e.g., "80% off...") - marketing item
        # Otherwise merge (handles orphaned order numbers like "749030039 (Outside the scope of VAT)")
        if ln[0].isupper():
            merged.append(ln)
        elif ln[0].isdigit() and '%' in ln[:5]:
            # Marketing line starting with percentage (e.g., "80% off £15 Offer Rebate")
            merged.append(ln)
        else:
            merged[-1] += " " + ln

    merged = [re.sub(r"\s{2,}", " ", s).strip() for s in merged]
    return [s for s in merged if s]


def extract_amounts(segment_text: str) -> List[float]:
    """Extract monetary amounts from the commission/refund segment."""
    if not segment_text:
        return []

    segment_text = (
        segment_text.replace("–", "-")
        .replace("- \n£", "-£")
        .replace("-\n£", "-£")
    )

    money_pattern = re.compile(
        r"([\-]?)\s*£\s*([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})"
    )
    results = []
    for m in money_pattern.finditer(segment_text):
        sign = -1 if m.group(1) == "-" else 1
        value = float(m.group(2).replace(",", "")) * sign
        
        if len(results) > 0 and value > 1000:
            break
            
        results.append(value)
    return results


def parse_reason_and_order(desc: str) -> Tuple[str, str]:
    """Extract refund reason and order number from a description."""
    m1 = re.search(r"Customer compensation for (.*?) query (\d+)", desc, re.I)
    if m1:
        return m1.group(1).strip(), m1.group(2).strip()

    m2 = re.search(
        r"Restaurant\s+Comp\s*[-–]?\s*Cancelled\s+Order\s*[-–\s]*?(\d+)", desc, re.I
    )
    if m2:
        return "Restaurant Comp - Cancelled Order", m2.group(1).strip()

    m3 = re.search(
        r"Order\s*ID[:\s]*([0-9]+)\s*[-–]\s*Partner\s+Compensation\s+Recook",
        desc,
        re.I,
    )
    if m3:
        return "Partner Compensation Recook", m3.group(1).strip()

    m4 = re.search(
        r"Order\s*ID[:\s]*(\d+)\s*[-–]\s*Customer\s+Compensation\s+Credit",
        desc,
        re.I,
    )
    if m4:
        return "Customer Compensation Credit", m4.group(1).strip()

    return "", ""


def build_refund_dataframe(descriptions: List[str], amounts: List[float]) -> pd.DataFrame:
    """Build a DataFrame from descriptions and amounts."""
    n = min(len(descriptions), len(amounts))
    rows = []
    for i in range(n):
        desc = descriptions[i]
        amt = amounts[i]
        reason, order = parse_reason_and_order(desc)
        rows.append({
            "index": i,
            "description": desc,
            "amount": amt,
            "reason": reason,
            "order_number": order,
            "outside_scope": "Outside the scope of VAT" in desc,
        })
    return pd.DataFrame(rows)


# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostic(pdf_path: Path) -> None:
    """Run full diagnostic trace on a PDF."""
    
    print("=" * 80)
    print(f"DIAGNOSTIC TRACE: {pdf_path.name}")
    print("=" * 80)
    
    # 1) Raw segment text
    print("\n" + "=" * 80)
    print("1. RAW SEGMENT TEXT (first 2000 chars)")
    print("=" * 80)
    segment = get_segment_text(pdf_path)
    print(segment[:2000])
    if len(segment) > 2000:
        print(f"\n... [{len(segment) - 2000} more characters]")
    
    # 2) Descriptions list
    print("\n" + "=" * 80)
    print("2. EXTRACTED DESCRIPTIONS (with indices)")
    print("=" * 80)
    descriptions = extract_descriptions(segment)
    for i, desc in enumerate(descriptions):
        # Truncate long descriptions for readability
        display_desc = desc[:100] + "..." if len(desc) > 100 else desc
        print(f"[{i:3d}] {display_desc}")
    print(f"\nTotal descriptions: {len(descriptions)}")
    
    # 3) Amounts list
    print("\n" + "=" * 80)
    print("3. EXTRACTED AMOUNTS (with indices)")
    print("=" * 80)
    amounts = extract_amounts(segment)
    for i, amt in enumerate(amounts):
        print(f"[{i:3d}] £{amt:,.2f}")
    print(f"\nTotal amounts: {len(amounts)}")
    
    # 4) Alignment check
    print("\n" + "=" * 80)
    print("4. ALIGNMENT CHECK")
    print("=" * 80)
    if len(descriptions) != len(amounts):
        print(f"⚠️  MISMATCH: {len(descriptions)} descriptions vs {len(amounts)} amounts")
        print(f"    Difference: {abs(len(descriptions) - len(amounts))}")
    else:
        print(f"✓  ALIGNED: {len(descriptions)} items each")
    
    # 5) Paired DataFrame
    print("\n" + "=" * 80)
    print("5. PAIRED DATAFRAME (description + amount + outside_scope)")
    print("=" * 80)
    df = build_refund_dataframe(descriptions, amounts)
    
    # Show all rows with key columns
    pd.set_option('display.max_colwidth', 60)
    pd.set_option('display.width', 200)
    print(df[["index", "amount", "outside_scope", "reason", "description"]].to_string())
    
    # 6) Marketing analysis
    print("\n" + "=" * 80)
    print("6. MARKETING ITEMS ANALYSIS")
    print("=" * 80)
    
    marketing_mask = (
        (~df["description"].str.contains("Commission", case=False, na=False))
        & (df["reason"].eq(""))
    )
    
    marketing_df = df[marketing_mask]
    
    if marketing_df.empty:
        print("No marketing items found")
    else:
        print(f"Found {len(marketing_df)} marketing item(s):\n")
        for _, row in marketing_df.iterrows():
            print(f"  Index: {row['index']}")
            print(f"  Amount: £{row['amount']:,.2f}")
            print(f"  Outside Scope: {row['outside_scope']}")
            print(f"  Description: {row['description']}")
            print()
        
        # Show the split
        marketing_vat = marketing_df[~marketing_df["outside_scope"]]
        marketing_no_vat = marketing_df[marketing_df["outside_scope"]]
        
        print(f"Marketing WITH VAT (outside_scope=False): {len(marketing_vat)} items, sum = £{marketing_vat['amount'].sum():,.2f}")
        print(f"Marketing NO VAT (outside_scope=True): {len(marketing_no_vat)} items, sum = £{marketing_no_vat['amount'].sum():,.2f}")
    
    # 7) Look for the rebate specifically
    print("\n" + "=" * 80)
    print("7. SEARCHING FOR REBATE/OFFER ITEMS")
    print("=" * 80)
    
    rebate_keywords = ["rebate", "offer", "80%", "discount"]
    for i, desc in enumerate(descriptions):
        desc_lower = desc.lower()
        if any(kw in desc_lower for kw in rebate_keywords):
            print(f"Found at index [{i}]: {desc}")
            if i < len(amounts):
                print(f"  Paired amount: £{amounts[i]:,.2f}")
            else:
                print(f"  ⚠️  No paired amount (index out of range)")
    
    # Also search raw segment for the rebate text
    print("\nSearching raw segment for '-£26.68'...")
    if "-£26.68" in segment or "- £26.68" in segment:
        # Find context around it
        for variant in ["-£26.68", "- £26.68"]:
            pos = segment.find(variant)
            if pos != -1:
                start = max(0, pos - 100)
                end = min(len(segment), pos + 50)
                print(f"Found at position {pos}:")
                print(f"  Context: ...{segment[start:end]}...")


if __name__ == "__main__":
    pdf_path = Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\05 Just Eat\02 PDFs\01 To Process\25.10.27 - JE Statement.pdf")
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    run_diagnostic(pdf_path)