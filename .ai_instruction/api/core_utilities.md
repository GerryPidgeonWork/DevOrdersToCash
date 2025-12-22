# Core Utilities (C06–C13)

> Last Updated: 2026-01-01

> General-purpose helper functions for common operations. These modules are the workhorses of any project.

**Who uses these:** Every script that needs to validate data, work with dates, manipulate strings, read/write files, process PDFs, create backups, or transform DataFrames.

---

## Conventions

**Return patterns:**
- Read functions → return the object (DataFrame, dict, string)
- Write functions → return the Path where the file was saved

**Logging:**
All functions log their actions via the central logger. Logs are informational side-effects; do not rely on them for control flow. Functions only raise exceptions when explicitly documented.

**Synchronous only:**
All I/O operations (C09, C10, C11) are synchronous. Async is not supported by design.

---

## Dependency Chain

```
C06_validation_utils    ← Depends on C00, C01, C02, C04
C07_datetime_utils      ← Depends on C00, C01
C08_string_utils        ← Depends on C00, C01
C09_io_utils            ← Depends on C00, C01, C06, C07
C10_pdf_utils           ← Depends on C00, C01
C11_file_backup         ← Depends on C00, C01, C02
C12_data_processing     ← Depends on C00, C01
C13_data_audit          ← Depends on C00, C01
```

---

## C06_validation_utils

**Purpose:** Centralised validation for files, directories, DataFrames, and configuration.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `validate_file_exists` | `(file_path: str \| Path) -> bool` | Returns `True` if exists; raises `FileNotFoundError` if not. |
| `validate_directory_exists` | `(dir_path: str \| Path, create_if_missing: bool = False) -> bool` | Returns `True` if exists; raises or creates based on flag. |
| `file_exists` | `(path: str \| Path) -> bool` | Returns `True`/`False` without raising. |
| `dir_exists` | `(path: str \| Path) -> bool` | Returns `True`/`False` without raising. |
| `validate_required_columns` | `(df: pd.DataFrame, required_cols: List[str]) -> bool` | Raises `ValueError` if columns missing. |
| `validate_non_empty` | `(data: Any, label: str = "Data") -> bool` | Raises `ValueError` if data is empty/None. |
| `validate_numeric` | `(df: pd.DataFrame, column: str) -> bool` | Raises `ValueError` if column is non-numeric. |
| `validate_config_keys` | `(section: str, keys: List[str]) -> bool` | Raises `KeyError` if config keys missing. |
| `validation_report` | `(results: Dict[str, bool]) -> None` | Logs PASS/FAIL summary for multiple validations. |

**Naming Convention:** Functions prefixed `validate_` raise exceptions on failure. Boolean helpers (e.g., `file_exists`, `dir_exists`) return `False` without raising.

### When to Use

- **Before reading files:** `validate_file_exists()`
- **Before processing DataFrames:** `validate_required_columns()`, `validate_non_empty()`
- **Conditional checks (no exception):** `file_exists()`, `dir_exists()`
- **Configuration validation at startup:** `validate_config_keys()`

### Example

```python
from core.C06_validation_utils import validate_file_exists, validate_required_columns, file_exists

# Raises if missing
validate_file_exists("data/orders.csv")

# Safe check
if file_exists("data/orders.csv"):
    df = read_csv_file("data/orders.csv")
    validate_required_columns(df, ["order_id", "amount", "date"])
```

---

## C07_datetime_utils

**Purpose:** Standardised date/time manipulation with ISO-style (YYYY-MM-DD) formatting.

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `DEFAULT_DATE_FORMAT` | `"%Y-%m-%d"` | Project-standard date format |

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `get_today` | `() -> date` | Returns today's date. |
| `get_now` | `() -> datetime` | Returns current datetime. |
| `as_str` | `(d: date \| datetime) -> str` | Converts to `YYYY-MM-DD` string. |
| `format_date` | `(d: date \| datetime, fmt: str = DEFAULT_DATE_FORMAT) -> str` | Custom format. |
| `parse_date` | `(value: str, fmt: str \| None = DEFAULT_DATE_FORMAT) -> date` | Parse string to date. `fmt=None` for auto-detection. |
| `timestamp_now` | `(fmt: str = "%Y%m%d_%H%M%S") -> str` | Filename-safe timestamp. |
| `get_start_of_week` | `(ref_date: date \| None = None) -> date` | Monday of the week. |
| `get_end_of_week` | `(ref_date: date \| None = None) -> date` | Sunday of the week. |
| `get_week_range` | `(ref_date: date \| None = None) -> Tuple[date, date]` | (Monday, Sunday) tuple. |
| `get_start_of_month` | `(ref_date: date \| None = None) -> date` | First day of month. |
| `get_end_of_month` | `(ref_date: date \| None = None) -> date` | Last day of month. |
| `get_month_range` | `(year: int, month: int) -> Tuple[date, date]` | (First, Last) of month. |
| `get_previous_month` | `(ref_date: date \| None = None) -> str` | Previous month as `YYYY-MM`. |
| `generate_date_range` | `(start: date, end: date) -> List[date]` | List of dates inclusive. |
| `is_within_range` | `(check_date: date, start_date: date, end_date: date) -> bool` | Inclusive range check. |
| `get_fiscal_quarter` | `(ref_date: date \| None = None) -> str` | Returns `"Q1 2025"` etc. |
| `get_week_id` | `(ref_date: date \| None = None) -> str` | ISO week as `"2025-W01"`. |

### Auto-Detection Formats (when `fmt=None`)

`parse_date()` tries these formats in order:
- `%Y-%m-%d` (2022-03-16)
- `%d/%m/%Y` (16/03/2022)
- `%d-%m-%Y`, `%d.%m.%Y`, `%Y/%m/%d`, `%m/%d/%Y`
- `%d-%b-%Y`, `%d-%b-%y`, `%b %d, %Y`, `%d %b %Y`

### Example

```python
from core.C07_datetime_utils import get_today, as_str, parse_date, get_fiscal_quarter, timestamp_now

today = get_today()
print(as_str(today))           # "2025-01-15"
print(get_fiscal_quarter())    # "Q1 2025"
print(timestamp_now())         # "20250115_143022"

# Auto-detect date format
d = parse_date("16/03/2022", fmt=None)
```

---

## C08_string_utils

**Purpose:** Text cleaning, normalisation, safe filename creation, and pattern extraction.

### Class

`StringUtils` — Namespace class with all methods as `@staticmethod`. Can use class or function facades.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `normalize_text` | `(text: str) -> str` | Lowercase, remove accents, collapse whitespace. |
| `slugify_filename` | `(filename: str, keep_extension: bool = True) -> str` | Safe filename with `[a-z0-9_]` only. |
| `make_safe_id` | `(text: str, max_length: int = 50) -> str` | Clean alphanumeric identifier. |
| `extract_pattern` | `(text: str, pattern: str, group: int \| None = None) -> str \| None` | Regex extraction. |
| `parse_number` | `(value: Any) -> float \| None` | Parse numeric from string (handles `£1,234.56`, `(123.45)`). |
| `clean_filename_generic` | `(original_name: str) -> str` | Standard filename cleanup. |
| `generate_dated_filename` | `(descriptor: str, extension: str = ".csv", start_date: date \| None = None, end_date: date \| None = None, frequency: str = "daily") -> str` | Date-prefixed filename. |

### Example

```python
from core.C08_string_utils import normalize_text, slugify_filename, generate_dated_filename, parse_number

clean = normalize_text("Café Report - März 2025.pdf")  # "cafe report marz 2025.pdf"
slug = slugify_filename("Monthly Report - 25.09.01.pdf")  # "monthly_report_25_09_01.pdf"

filename = generate_dated_filename("Orders Export", ".csv")  # "2025-01-15_orders_export.csv"
filename = generate_dated_filename("Weekly", frequency="range", start_date=d1, end_date=d2)

amount = parse_number("£1,234.56")  # 1234.56
amount = parse_number("(500.00)")   # -500.0 (accounting negative)
```

---

## C09_io_utils

**Purpose:** File I/O for CSV, JSON, and Excel with validation, logging, and backup support.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `read_csv_file` | `(file_path: str \| Path, **kwargs) -> pd.DataFrame` | Read CSV with validation. |
| `save_dataframe` | `(df: pd.DataFrame, file_path: str \| Path, overwrite: bool = True, backup_existing: bool = True, index: bool = False, **kwargs) -> Path` | Save DataFrame to CSV with optional backup. |
| `read_json` | `(file_path: str \| Path, encoding: str = "utf-8") -> Dict[str, Any]` | Read JSON file. |
| `save_json` | `(data: Dict \| List, file_path: str \| Path, indent: int = 4, overwrite: bool = True, encoding: str = "utf-8") -> Path` | Save JSON file. |
| `save_excel` | `(df: pd.DataFrame, file_path: str \| Path, sheet_name: str = "Sheet1", index: bool = False, **kwargs) -> Path` | Save DataFrame to Excel. |
| `get_latest_file` | `(directory: str \| Path, pattern: str = "*") -> Path \| None` | Find most recently modified file. |
| `append_to_file` | `(file_path: str \| Path, text: str, newline: bool = True) -> Path` | Append text to file. |

### Key Behaviours

- **Auto-creates directories** before writing
- **Validates file exists** before reading
- **Creates timestamped backups** when `backup_existing=True`
- **Generates versioned filenames** when `overwrite=False`

### Example

```python
from core.C09_io_utils import read_csv_file, save_dataframe, read_json, save_json, get_latest_file

# CSV
df = read_csv_file("data/orders.csv")
save_dataframe(df, "outputs/orders_cleaned.csv")  # Auto-backup if exists

# JSON
config = read_json("config/settings.json")
save_json({"processed": True}, "outputs/status.json")

# Find latest
latest = get_latest_file("data/", "*.csv")
```

---

## C10_pdf_utils

**Purpose:** PDF text extraction, manipulation, table extraction, and validation.

### Class

`PDFUtils` — Namespace class with all methods as `@staticmethod`. Can use class or function facades.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `extract_pdf_text` | `(file_path: str \| Path) -> str` | Extract all text from PDF. |
| `extract_pdf_text_by_page` | `(file_path: str \| Path) -> List[str]` | List of text per page. |
| `get_pdf_page_count` | `(file_path: str \| Path) -> int` | Number of pages. |
| `extract_field` | `(text: str, pattern: str, group: int = 1) -> str \| None` | Regex field extraction. |
| `extract_all_fields` | `(text: str, pattern: str) -> List[str]` | All regex matches. |
| `rotate_pdf` | `(file_path: str \| Path, degrees: int, output_path: str \| Path \| None = None) -> Path` | Rotate all pages. |
| `merge_pdfs` | `(input_paths: List[str \| Path], output_path: str \| Path) -> Path` | Combine multiple PDFs. |
| `extract_pages` | `(file_path: str \| Path, page_numbers: List[int], output_path: str \| Path) -> Path` | Extract specific pages. |
| `extract_pages_matching` | `(file_path: str \| Path, pattern: str, output_path: str \| Path) -> Path` | Extract pages containing pattern. |
| `remove_pages_containing` | `(file_path: str \| Path, pattern: str, output_path: str \| Path) -> Path` | Remove pages matching pattern. |
| `extract_tables` | `(file_path: str \| Path, pages: str = "all") -> List[List[List[str]]]` | Raw table data via pdfplumber. |
| `extract_tables_to_dataframe` | `(file_path: str \| Path, pages: str = "all", table_index: int = 0) -> pd.DataFrame` | Table as DataFrame. |
| `is_valid_pdf` | `(file_path: str \| Path) -> bool` | Check if file is valid PDF. |

### Example

```python
from core.C10_pdf_utils import extract_pdf_text, extract_field, merge_pdfs, extract_tables_to_dataframe

# Extract text and field
text = extract_pdf_text("invoices/invoice_001.pdf")
invoice_no = extract_field(text, r"Invoice No\.?\s*(\S+)")

# Merge PDFs
merge_pdfs(["part1.pdf", "part2.pdf"], "combined.pdf")

# Extract table as DataFrame
df = extract_tables_to_dataframe("report.pdf", pages="1", table_index=0)
```

---

## C11_file_backup

**Purpose:** Timestamped backups with MD5 checksums, compression, and retention policies.

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `BACKUP_DIR` | `PROJECT_ROOT / "backups"` | Default backup location |

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `compute_md5` | `(file_path: str \| Path) -> str` | Calculate MD5 hash. |
| `ensure_backup_dir` | `(backup_dir: Path \| None = None) -> Path` | Create backup directory. |
| `create_backup` | `(file_path: str \| Path, backup_dir: Path \| None = None) -> Path` | Timestamped copy with metadata. |
| `create_zipped_backup` | `(file_path: str \| Path, backup_dir: Path \| None = None) -> Path` | Compressed backup. |
| `list_backups` | `(original_name: str, backup_dir: Path \| None = None) -> List[Path]` | Find all backups for a file. |
| `purge_old_backups` | `(original_name: str, keep: int = 5, backup_dir: Path \| None = None) -> int` | Delete old backups, keep N newest. |
| `restore_backup` | `(backup_path: str \| Path, restore_to: str \| Path) -> Path` | Restore backup to location. |

### Example

```python
from core.C11_file_backup import create_backup, create_zipped_backup, list_backups, purge_old_backups

# Create backup
backup_path = create_backup("data/important.csv")

# Compressed backup
zip_path = create_zipped_backup("data/important.csv")

# List and purge
backups = list_backups("important.csv")
deleted = purge_old_backups("important.csv", keep=3)
```

---

## C12_data_processing

**Purpose:** DataFrame cleaning, standardisation, merging, and summarisation.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `standardise_columns` | `(df: pd.DataFrame) -> pd.DataFrame` | Lowercase, strip, replace spaces with underscores. |
| `convert_to_datetime` | `(df: pd.DataFrame, columns: List[str], **kwargs) -> pd.DataFrame` | Convert columns to datetime. |
| `fill_missing` | `(df: pd.DataFrame, columns: List[str], value: Any = 0) -> pd.DataFrame` | Fill NaN with value. |
| `remove_duplicates` | `(df: pd.DataFrame, subset: List[str] \| None = None, keep: str = "first") -> pd.DataFrame` | Drop duplicate rows. |
| `filter_rows` | `(df: pd.DataFrame, column: str, values: List[Any], exclude: bool = False) -> pd.DataFrame` | Keep/exclude rows by value. |
| `merge_dataframes` | `(left: pd.DataFrame, right: pd.DataFrame, on: str \| List[str], how: str = "inner") -> pd.DataFrame` | Merge with logging. |
| `summarise_numeric` | `(df: pd.DataFrame) -> pd.DataFrame` | Describe numeric columns. |

### Example

```python
from core.C12_data_processing import standardise_columns, convert_to_datetime, remove_duplicates, merge_dataframes

df = standardise_columns(df)  # Column names: "Order ID" -> "order_id"
df = convert_to_datetime(df, ["order_date", "ship_date"])
df = remove_duplicates(df, subset=["order_id"])

merged = merge_dataframes(orders, customers, on="customer_id", how="left")
```

---

## C13_data_audit

**Purpose:** DataFrame comparison, missing row detection, and reconciliation.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `get_missing_rows` | `(source: pd.DataFrame, target: pd.DataFrame, key_columns: List[str]) -> pd.DataFrame` | Rows in source not in target. |
| `compare_dataframes` | `(df1: pd.DataFrame, df2: pd.DataFrame, key_columns: List[str]) -> Dict[str, pd.DataFrame]` | Returns `{"only_in_df1", "only_in_df2", "in_both"}`. |
| `reconcile_column_sums` | `(df1: pd.DataFrame, df2: pd.DataFrame, columns: List[str]) -> pd.DataFrame` | Compare column totals. |
| `summarise_differences` | `(comparison: Dict[str, pd.DataFrame]) -> Dict[str, int]` | Row counts from compare result. |
| `log_audit_summary` | `(summary: Dict[str, int], label: str = "Audit") -> None` | Log the summary. |

### Example

```python
from core.C13_data_audit import compare_dataframes, reconcile_column_sums, summarise_differences, log_audit_summary

# Compare two datasets
comparison = compare_dataframes(expected_df, actual_df, key_columns=["order_id"])
summary = summarise_differences(comparison)
log_audit_summary(summary, label="Orders Reconciliation")

# Check column totals match
recon = reconcile_column_sums(expected_df, actual_df, columns=["amount", "quantity"])
```

---

## Summary Table

| Module | Exports | Primary Use |
|--------|---------|-------------|
| C06 | 9 | Validation (files, directories, DataFrames, config) |
| C07 | 18 | Date/time formatting, parsing, ranges, fiscal periods |
| C08 | 8 | String cleaning, filename generation, pattern extraction |
| C09 | 7 | File I/O (CSV, JSON, Excel) with logging and backup |
| C10 | 14 | PDF text extraction, manipulation, table extraction |
| C11 | 8 | Timestamped backups with MD5, compression, retention |
| C12 | 7 | DataFrame cleaning, standardisation, merging |
| C13 | 5 | DataFrame comparison and reconciliation |

**Total: 76 exports**

> *Export counts are indicative. `__all__` in each module's source code is authoritative.*