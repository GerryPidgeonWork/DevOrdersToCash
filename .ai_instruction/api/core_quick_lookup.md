# Quick Lookup — Task → Function

> Last Updated: 2026-01-01

> Find the right function fast. Organised by task, not by module.

**Rule:** If a function exists here, use it. Do not reimplement.

**Important:** If a task is not listed here, you MUST still search the detailed Core docs (`core_foundation.md`, `core_utilities.md`, `core_integrations.md`) before implementing. Absence from this index does not mean absence from Core.

---

## 📦 Imports & Packages

| I need to... | Use | From |
|--------------|-----|------|
| Import pandas, numpy, requests, etc. | `from core.C00_set_packages import *` | C00 |
| Import GUI packages (G00–G04 framework) | `from gui.G00a_gui_packages import *` | G00a |
| Import GUI packages (Gx0+ pages) | `from gui.G02a_widget_primitives import *` | G02a |
| Get the logger for my module | `logger = get_logger(__name__)` | C01 |
| Log an exception with traceback | `log_exception(exc, context="...")` | C01 |
| Initialise logging at startup | `init_logging()` | C01 |
| Add visual divider in logs | `log_divider("info", "SECTION HEADER")` | C01 |

---

## 📁 Files & Directories

| I need to... | Use | From |
|--------------|-----|------|
| Get project root path | `PROJECT_ROOT` | C02 |
| Get data/outputs/logs/config directory | `DATA_DIR`, `OUTPUTS_DIR`, `LOGS_DIR`, `CONFIG_DIR` | C02 |
| Build a file path from parts | `build_path(dir, "subdir", "file.csv")` | C02 |
| Ensure a directory exists | `ensure_directory(path)` | C02 |
| Generate a unique temp file path | `get_temp_file(suffix=".csv")` | C02 |
| Check if file exists (raises) | `validate_file_exists(path)` | C06 |
| Check if file exists (bool) | `file_exists(path)` | C06 |
| Check if directory exists (raises) | `validate_directory_exists(path)` | C06 |
| Check if directory exists (bool) | `dir_exists(path)` | C06 |
| Find the latest file in a folder | `get_latest_file(directory, "*.csv")` | C09 |
| Append text to a file | `append_to_file(path, text)` | C09 |

---

## 📄 Reading Files

| I need to... | Use | From |
|--------------|-----|------|
| Read a CSV to DataFrame | `read_csv_file(path)` | C09 |
| Read a JSON file to dict | `read_json(path)` | C09 |
| Extract text from PDF | `extract_pdf_text(path)` | C10 |
| Extract text per page from PDF | `extract_pdf_text_by_page(path)` | C10 |
| Get PDF page count | `get_pdf_page_count(path)` | C10 |
| Extract tables from PDF | `extract_tables(path)` | C10 |
| Extract PDF table as DataFrame | `extract_tables_to_dataframe(path)` | C10 |
| Check if PDF is valid | `is_valid_pdf(path)` | C10 |
| Load from cache | `load_cache(name, fmt="json")` | C15 |

---

## 💾 Writing Files

| I need to... | Use | From |
|--------------|-----|------|
| Save DataFrame to CSV | `save_dataframe(df, path)` | C09 |
| Save DataFrame to Excel | `save_excel(df, path)` | C09 |
| Save dict/list to JSON | `save_json(data, path)` | C09 |
| Save to cache | `save_cache(name, data, fmt="json")` | C15 |
| Clear cache | `clear_cache(name)` or `clear_cache()` | C15 |

---

## 📋 PDF Manipulation

| I need to... | Use | From |
|--------------|-----|------|
| Extract a field with regex | `extract_field(text, r"Invoice:\s*(\S+)")` | C10 |
| Extract all regex matches | `extract_all_fields(text, pattern)` | C10 |
| Rotate PDF pages | `rotate_pdf(path, degrees)` | C10 |
| Merge multiple PDFs | `merge_pdfs([path1, path2], output_path)` | C10 |
| Extract specific pages | `extract_pages(path, [1, 3, 5], output_path)` | C10 |
| Extract pages matching text | `extract_pages_matching(path, pattern, output)` | C10 |
| Remove pages containing text | `remove_pages_containing(path, pattern, output)` | C10 |

---

## 🗓️ Dates & Times

| I need to... | Use | From |
|--------------|-----|------|
| Get today's date | `get_today()` | C07 |
| Get current datetime | `get_now()` | C07 |
| Format date as YYYY-MM-DD | `as_str(date_obj)` | C07 |
| Format date with custom format | `format_date(date_obj, fmt)` | C07 |
| Parse string to date | `parse_date(string)` or `parse_date(string, fmt=None)` | C07 |
| Get filename-safe timestamp | `timestamp_now()` | C07 |
| Get start of week (Monday) | `get_start_of_week(date)` | C07 |
| Get end of week (Sunday) | `get_end_of_week(date)` | C07 |
| Get week range tuple | `get_week_range(date)` | C07 |
| Get start of month | `get_start_of_month(date)` | C07 |
| Get end of month | `get_end_of_month(date)` | C07 |
| Get month range tuple | `get_month_range(year, month)` | C07 |
| Get previous month string | `get_previous_month()` | C07 |
| Generate list of dates | `generate_date_range(start, end)` | C07 |
| Check if date in range | `is_within_range(date, start, end)` | C07 |
| Get fiscal quarter label | `get_fiscal_quarter(date)` | C07 |
| Get ISO week ID | `get_week_id(date)` | C07 |

---

## 🔤 Strings & Filenames

| I need to... | Use | From |
|--------------|-----|------|
| Normalise text (lowercase, no accents) | `normalize_text(text)` | C08 |
| Make filename safe | `slugify_filename(filename)` | C08 |
| Make a safe ID from text | `make_safe_id(text)` | C08 |
| Extract pattern with regex | `extract_pattern(text, pattern)` | C08 |
| Parse number from string | `parse_number("£1,234.56")` | C08 |
| Clean filename | `clean_filename_generic(filename)` | C08 |
| Generate dated filename | `generate_dated_filename("Report", ".csv")` | C08 |

---

## ✅ Validation

| I need to... | Use | From |
|--------------|-----|------|
| Validate required DataFrame columns | `validate_required_columns(df, ["col1", "col2"])` | C06 |
| Validate DataFrame not empty | `validate_non_empty(df, label="Orders")` | C06 |
| Validate column is numeric | `validate_numeric(df, "amount")` | C06 |
| Validate config keys exist | `validate_config_keys("snowflake", ["user", "account"])` | C06 |
| Log validation summary | `validation_report({"check1": True, "check2": False})` | C06 |

---

## 🔧 DataFrame Processing

| I need to... | Use | From |
|--------------|-----|------|
| Standardise column names | `standardise_columns(df)` | C12 |
| Convert columns to datetime | `convert_to_datetime(df, ["date_col"])` | C12 |
| Fill missing values | `fill_missing(df, ["col"], value=0)` | C12 |
| Remove duplicate rows | `remove_duplicates(df, subset=["id"])` | C12 |
| Filter rows by values | `filter_rows(df, "status", ["active", "pending"])` | C12 |
| Merge two DataFrames | `merge_dataframes(left, right, on="id")` | C12 |
| Summarise numeric columns | `summarise_numeric(df)` | C12 |

---

## 🔍 Data Audit & Comparison

| I need to... | Use | From |
|--------------|-----|------|
| Find rows in A not in B | `get_missing_rows(source, target, ["key"])` | C13 |
| Compare two DataFrames | `compare_dataframes(df1, df2, ["key"])` | C13 |
| Compare column totals | `reconcile_column_sums(df1, df2, ["amount"])` | C13 |
| Summarise comparison result | `summarise_differences(comparison)` | C13 |
| Log audit summary | `log_audit_summary(summary, label="Recon")` | C13 |

---

## 🗄️ Backup & Restore

| I need to... | Use | From |
|--------------|-----|------|
| Create timestamped backup | `create_backup(file_path)` | C11 |
| Create compressed backup | `create_zipped_backup(file_path)` | C11 |
| List backups for a file | `list_backups(original_name)` | C11 |
| Delete old backups | `purge_old_backups(original_name, keep=5)` | C11 |
| Restore a backup | `restore_backup(backup_path, restore_to)` | C11 |
| Compute MD5 hash | `compute_md5(file_path)` | C11 |

---

## ⚙️ Configuration

| I need to... | Use | From |
|--------------|-----|------|
| Load config at startup | `initialise_config()` | C04 |
| Get a config value | `get_config("section", "key", default=None)` | C04 |
| Reload config from disk | `reload_config()` | C04 |
| Access full config dict | `CONFIG["section"]["key"]` | C04 |

---

## 🖥️ System & OS

| I need to... | Use | From |
|--------------|-----|------|
| Detect operating system | `detect_os()` | C03 |
| Get user's Downloads folder | `user_download_folder()` | C03 |
| Install global exception hook | `install_global_exception_hook()` | C05 |
| Handle error (potentially fatal) | `handle_error(exc, context="...", fatal=False)` | C05 |
| Raise test error for debugging | `simulate_error()` | C05 |

---

## ❄️ Snowflake

| I need to... | Use | From |
|--------------|-----|------|
| Connect to Snowflake (SSO) | `connect_to_snowflake("user@domain.com")` | C14 |
| Set role/warehouse context | `set_snowflake_context(conn, role, warehouse)` | C14 |
| Run raw SQL query | `run_query(conn, sql)` | C14 |
| Load SQL file from /sql/ | `load_sql_file("query.sql", params={...})` | C14 |
| Run SQL file | `run_sql_file(conn, "query.sql", params={...})` | C14 |
| Run SQL to DataFrame | `run_sql_to_dataframe(conn, sql)` | C14 |
| Run SQL file to DataFrame | `run_sql_file_to_dataframe(conn, "query.sql")` | C14 |

---

## 🌐 REST APIs

| I need to... | Use | From |
|--------------|-----|------|
| Make HTTP request with retry | `api_request("GET", url, headers=...)` | C17 |
| GET JSON from API | `get_json(url, headers=...)` | C17 |
| POST JSON to API | `post_json(url, json_data, headers=...)` | C17 |
| Build auth header | `get_auth_header(token)` | C17 |

---

## ⚡ Parallel Execution

| I need to... | Use | From |
|--------------|-----|------|
| Run tasks in parallel | `run_in_parallel(func, tasks, mode="thread")` | C16 |
| Split list into chunks | `chunk_tasks(task_list, chunk_size)` | C16 |
| Run batches with delay | `run_batches(func, tasks, chunk_size=20, delay=0.5)` | C16 |

---

## 🌍 Web Automation (Selenium)

| I need to... | Use | From |
|--------------|-----|------|
| Create Chrome WebDriver | `get_chrome_driver(headless=True)` | C18 |
| Wait for element | `wait_for_element(driver, "id", "btn")` | C18 |
| Scroll to page bottom | `scroll_to_bottom(driver)` | C18 |
| Click element safely | `click_element(driver, element)` | C18 |
| Close WebDriver | `close_driver(driver)` | C18 |

---

## 📂 Google Drive

| I need to... | Use | From |
|--------------|-----|------|
| Check if Drive App installed | `is_google_drive_installed()` | C19 |
| List Drive accounts | `get_google_drive_accounts()` | C19 |
| Extract drive root from path | `extract_drive_root(path)` | C19 |
| Authenticate with Drive API | `get_drive_service()` | C19 |
| Find folder ID by name | `find_folder_id(service, "Reports")` | C19 |
| Find file ID by name | `find_file_id(service, "report.xlsx")` | C19 |
| Upload file | `upload_file(service, local_path, folder_id)` | C19 |
| Upload DataFrame as CSV | `upload_dataframe_as_csv(service, buffer, name)` | C19 |
| Download file by ID | `download_file(service, file_id, local_path)` | C19 |

---

## 🪟 GUI Helpers

| I need to... | Use | From |
|--------------|-----|------|
| Show info popup | `show_info("Message")` | C20 |
| Show warning popup | `show_warning("Message")` | C20 |
| Show error popup | `show_error("Message")` | C20 |
| Create progress dialog | `ProgressPopup(parent, "Loading...")` | C20 |
| Run task in background thread | `run_in_thread(func, *args)` | C20 |
| Access GUI theme colours | `GUI_THEME["bg"]`, `GUI_THEME["accent"]` | C20 |

---

## ❌ Anti-Patterns — Never Do This

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| `import pandas as pd` | `from core.C00_set_packages import *` |
| `import numpy as np` | `from core.C00_set_packages import *` |
| `from pathlib import Path; root = Path(__file__).parent.parent` | `from core.C02_set_file_paths import PROJECT_ROOT` |
| `pd.read_csv(path)` | `read_csv_file(path)` from C09 |
| `df.to_csv(path)` | `save_dataframe(df, path)` from C09 |
| `json.load(open(path))` | `read_json(path)` from C09 |
| `datetime.now().strftime(...)` | `timestamp_now()` or `as_str(get_now())` from C07 |
| `os.path.exists(path)` | `file_exists(path)` or `dir_exists(path)` from C06 |
| `os.makedirs(path, exist_ok=True)` | `ensure_directory(path)` from C02 |
| `print("Debug message")` | `logger.info("Debug message")` from C01 |
| Implement your own retry logic | `api_request(..., retries=3)` from C17 |
| Write parallel execution from scratch | `run_in_parallel(...)` from C16 |

---

## 🔢 Module Reference

| Module | Purpose | Exports |
|--------|---------|---------|
| C00 | Package hub | 75 |
| C01 | Logging | 12 |
| C02 | File paths | 25 |
| C03 | System/OS | 2 |
| C04 | Config loader | 8 |
| C05 | Error handler | 4 |
| C06 | Validation | 9 |
| C07 | Date/time | 18 |
| C08 | Strings | 8 |
| C09 | File I/O | 7 |
| C10 | PDF utils | 14 |
| C11 | Backups | 8 |
| C12 | Data processing | 7 |
| C13 | Data audit | 5 |
| C14 | Snowflake | 13 |
| C15 | Cache | 7 |
| C16 | Parallel | 3 |
| C17 | REST API | 4 |
| C18 | Selenium | 5 |
| C19 | Google Drive | 12 |
| C20 | GUI helpers | 6 |

**Total: 252 exports**