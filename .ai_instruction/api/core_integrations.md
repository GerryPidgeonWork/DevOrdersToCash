# Core Integrations (C14–C20)

> Last Updated: 2026-01-01

> External service connectors, concurrency utilities, and GUI helpers. These modules handle connections to databases, APIs, cloud storage, and browser automation.

**Who uses these:** Scripts that need to query Snowflake, call REST APIs, automate browsers, interact with Google Drive, run parallel tasks, or display GUI popups.

---

## Conventions

**Authentication:**
All services requiring credentials (Snowflake, Google Drive) use OAuth or SSO flows. Credentials are stored in `/credentials/` and never hardcoded.

**Connection lifecycle:**
Functions that create connections (Snowflake, Selenium) return the connection object. The caller is responsible for closing/cleanup.

> ⚠️ **Connection Cleanup:** Always close connections in a `finally` block or use context managers where available. Unclosed connections leak resources and may cause application instability.

**Error handling:**
Integration-layer functions (C14–C20) typically log errors and return `None` on recoverable external failures (e.g., API timeout, connection refused). This allows callers to check return values and handle gracefully. Validation utilities (C06) and fatal error handlers (C05) may raise exceptions as documented in their respective modules.

---

## Dependency Chain

```
C14_snowflake_connector      ← Depends on C00, C01, C02, C04
C15_cache_manager            ← Depends on C00, C01, C02, C06
C16_parallel_executor        ← Depends on C00, C01
C17_api_manager              ← Depends on C00, C01
C18_web_automation           ← Depends on C00, C01, C03
C19_google_drive_integration ← Depends on C00, C01, C02, C03
C20_gui_helpers              ← Depends on C00, C01 (+ tkinter)
```

---

## C14_snowflake_connector

**Purpose:** Secure Snowflake connections via Okta SSO, SQL file execution, and DataFrame results.

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `SNOWFLAKE_ACCOUNT` | `"HC77929-GOPUFF"` | Snowflake account identifier |
| `SNOWFLAKE_EMAIL_DOMAIN` | `"gopuff.com"` | Required email domain |
| `CONTEXT_PRIORITY` | List of role/warehouse dicts | Auto-selection priority |
| `DEFAULT_DATABASE` | `"DBT_PROD"` | Default database |
| `DEFAULT_SCHEMA` | `"CORE"` | Default schema |

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `get_snowflake_credentials` | `(email_address: str) -> Dict[str, Any] \| None` | Build credential dict for SSO. |
| `set_snowflake_context` | `(conn, role: str, warehouse: str, database: str = DEFAULT_DATABASE, schema: str = DEFAULT_SCHEMA) -> bool` | Apply role/warehouse/database/schema. |
| `connect_to_snowflake` | `(email_address: str) -> Any \| None` | Establish SSO connection with auto-context. |
| `run_query` | `(conn, sql: str, fetch: bool = True) -> Any \| None` | Execute raw SQL, optionally fetch results. |
| `load_sql_file` | `(file_name: str, params: Dict[str, Any] \| None = None) -> str` | Load SQL from `/sql/` with parameter substitution. |
| `run_sql_file` | `(conn, file_name: str, params: Dict \| None = None, fetch: bool = True) -> Any` | Load and execute SQL file. |
| `run_sql_to_dataframe` | `(conn, sql: str, standardise: bool = True) -> pd.DataFrame \| None` | Execute SQL, return DataFrame. |
| `run_sql_file_to_dataframe` | `(conn, file_name: str, params: Dict \| None = None, standardise: bool = True) -> pd.DataFrame \| None` | Load SQL file, return DataFrame. |

### SQL Parameter Substitution

SQL files use Python `str.format()` placeholders:
```sql
-- orders_summary.sql
SELECT * FROM orders WHERE order_date >= '{start_date}'
```

```python
df = run_sql_file_to_dataframe(conn, "orders_summary.sql", params={"start_date": "2025-01-01"})
```

### Example

```python
from core.C14_snowflake_connector import connect_to_snowflake, run_sql_file_to_dataframe

conn = connect_to_snowflake("user@gopuff.com")
if conn:
    df = run_sql_file_to_dataframe(conn, "orders_summary.sql", params={"start_date": "2025-01-01"})
    conn.close()
```

---

## C15_cache_manager

**Purpose:** Local file caching for JSON, CSV, and pickle formats with save/load/clear operations.

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `CACHE_DIR` | `PROJECT_ROOT / "cache"` | Cache storage location |

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `ensure_cache_dir` | `() -> Path` | Create cache directory if missing. |
| `get_cache_path` | `(name: str, fmt: str = "json") -> Path` | Build full path to cache file. |
| `save_cache` | `(name: str, data: Any, fmt: str = "json") -> Path \| None` | Save data to cache. |
| `load_cache` | `(name: str, fmt: str = "json") -> Any` | Load cached data (or None if missing). |
| `clear_cache` | `(name: str \| None = None) -> None` | Delete one cache or all caches. |
| `list_cache_files` | `() -> list[Path]` | List all cached files. |

### Supported Formats

| Format | Extension | Data Type |
|--------|-----------|-----------|
| `"json"` | `.json` | Dict, List |
| `"csv"` | `.csv` | pd.DataFrame |
| `"pkl"` | `.pkl` | Any Python object |

### Example

```python
from core.C15_cache_manager import save_cache, load_cache, clear_cache

# Cache API response
save_cache("api_response", {"data": [1, 2, 3]}, fmt="json")

# Cache DataFrame
save_cache("orders_today", df, fmt="csv")

# Load cache (returns None if missing)
cached = load_cache("api_response")

# Clear specific cache
clear_cache("api_response")

# Clear all caches
clear_cache()
```

---

## C16_parallel_executor

**Purpose:** Concurrent task execution using threads or processes with progress tracking.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `run_in_parallel` | `(func, tasks: List[Any], mode: str = "thread", max_workers: int = 8, show_progress: bool = True) -> List[Any]` | Execute tasks concurrently. |
| `chunk_tasks` | `(task_list: List[Any], chunk_size: int) -> List[List[Any]]` | Split list into chunks. |
| `run_batches` | `(func, all_tasks: List[Any], chunk_size: int = 20, delay: float = 0.5) -> List[Any]` | Execute in sequential batches with delay. |

### Mode Selection

| Mode | Use Case |
|------|----------|
| `"thread"` | I/O-bound tasks (API calls, file reads) |
| `"process"` | CPU-bound tasks (data transforms, calculations) |

### Example

```python
from core.C16_parallel_executor import run_in_parallel, run_batches
from core.C17_api_manager import get_json

# Parallel API calls (I/O-bound)
def fetch_url(url):
    return get_json(url)

results = run_in_parallel(fetch_url, url_list, mode="thread", max_workers=10)

# Rate-limited API with batches
results = run_batches(fetch_url, url_list, chunk_size=20, delay=1.0)
```

---

## C17_api_manager

**Purpose:** REST API request wrapper with retries, timeouts, and structured logging.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `api_request` | `(method: str, url: str, headers: Dict \| None = None, params: Dict \| None = None, data: Dict \| None = None, json_data: Dict \| None = None, retries: int = 3, timeout: int = 15) -> requests.Response \| None` | Generic HTTP request with retry. |
| `get_json` | `(url: str, headers: Dict \| None = None, params: Dict \| None = None) -> Dict \| None` | GET request, return parsed JSON. |
| `post_json` | `(url: str, json_data: Dict, headers: Dict \| None = None) -> Dict \| None` | POST JSON payload, return parsed response. |
| `get_auth_header` | `(token: str, bearer: bool = True) -> Dict[str, str]` | Build Authorization header. |

### Retry Behaviour

- 3 retries by default
- 2-second delay between retries
- Logs truncated response on failure

### Example

```python
from core.C17_api_manager import get_json, post_json, get_auth_header

# Simple GET
data = get_json("https://api.example.com/users")

# Authenticated POST
headers = get_auth_header("my_api_token")
response = post_json("https://api.example.com/orders", {"item": "widget"}, headers=headers)
```

---

## C18_web_automation

**Purpose:** Selenium WebDriver setup and browser automation helpers.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `get_chrome_driver` | `(profile_name: str \| None = None, headless: bool = False) -> Any` | Create configured Chrome WebDriver. |
| `wait_for_element` | `(driver, by: str, selector: str, timeout: int = 10) -> Any` | Wait for element presence. |
| `scroll_to_bottom` | `(driver, pause_time: float = 1.0) -> None` | Scroll page to bottom (for lazy-loading). |
| `click_element` | `(driver, element) -> bool` | Safe click with logging. |
| `close_driver` | `(driver) -> None` | Safely close WebDriver. |

### Locator Strategies (for `wait_for_element`)

| `by` value | Selenium equivalent |
|------------|---------------------|
| `"id"` | `By.ID` |
| `"xpath"` | `By.XPATH` |
| `"css_selector"` | `By.CSS_SELECTOR` |
| `"name"` | `By.NAME` |
| `"class_name"` | `By.CLASS_NAME` |

### Example

```python
from core.C18_web_automation import get_chrome_driver, wait_for_element, close_driver

driver = get_chrome_driver(headless=True)
if driver:
    driver.get("https://example.com")
    element = wait_for_element(driver, "id", "submit-button", timeout=10)
    if element:
        element.click()
    close_driver(driver)
```

---

## C19_google_drive_integration

**Purpose:** Google Drive App detection and Google Drive API operations (upload, download, search).

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `SCOPES` | `["https://www.googleapis.com/auth/drive"]` | OAuth scope |

### Functions — Local Drive Detection

| Function | Signature | Use |
|----------|-----------|-----|
| `is_google_drive_installed` | `() -> bool` | Check if Google Drive App is installed. |
| `get_google_drive_accounts` | `() -> List[Dict[str, str]]` | List configured accounts with email and root path. |
| `extract_drive_root` | `(path: Path \| str) -> str` | Extract drive root from nested path. |

### Functions — Google Drive API

| Function | Signature | Use |
|----------|-----------|-----|
| `get_drive_service` | `() -> Resource \| None` | Authenticate and return Drive API service. |
| `find_folder_id` | `(service, folder_name: str) -> str \| None` | Find folder ID by name. |
| `find_file_id` | `(service, file_name: str, in_folder_id: str \| None = None) -> str \| None` | Find file ID by name. |
| `upload_file` | `(service, local_path: Path, folder_id: str \| None = None, filename: str \| None = None) -> str \| None` | Upload local file. |
| `upload_dataframe_as_csv` | `(service, csv_buffer: io.StringIO, filename: str, folder_id: str \| None = None) -> str \| None` | Upload DataFrame as CSV from memory. |
| `download_file` | `(service, file_id: str, local_path: Path) -> None` | Download file by ID. |

### Authentication Setup

Requires OAuth credentials from Google Cloud Console:
1. Create project in Google Cloud Console
2. Enable Drive API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to `/credentials/`

First run triggers browser authentication; subsequent runs use cached `token.json`.

### Example

```python
from core.C19_google_drive_integration import get_drive_service, find_folder_id, upload_file

service = get_drive_service()
if service:
    folder_id = find_folder_id(service, "Reports")
    file_id = upload_file(service, Path("outputs/report.xlsx"), folder_id=folder_id)
```

---

## C20_gui_helpers

**Purpose:** Lightweight GUI utilities for Tkinter applications — popups, progress bars, threading.

**Note:** This module imports `tkinter`. Use only in GUI contexts.

### Constants

| Name | Type | Contents |
|------|------|----------|
| `GUI_THEME` | `Dict` | `bg`, `fg`, `accent`, `success`, `warning`, `error`, `font`, `font_bold` |

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `show_info` | `(message: str, title: str = "Information") -> None` | Info popup. |
| `show_warning` | `(message: str, title: str = "Warning") -> None` | Warning popup. |
| `show_error` | `(message: str, title: str = "Error") -> None` | Error popup. |
| `run_in_thread` | `(target: Callable, *args, **kwargs) -> threading.Thread` | Run function in daemon thread. |

### Class: ProgressPopup

Modal progress dialog with percentage display.

```python
class ProgressPopup:
    def __init__(self, parent: tk.Tk, message: str = "Processing...") -> None
    def update_progress(self, current: int, total: int) -> None
    # Supports context manager (with statement)
```

### Example

```python
from core.C20_gui_helpers import show_info, show_error, ProgressPopup, run_in_thread

# Simple popups
show_info("Operation completed successfully.")
show_error("Failed to connect to database.")

# Progress dialog
with ProgressPopup(root, "Importing data...") as progress:
    for i, row in enumerate(rows):
        process(row)
        progress.update_progress(i + 1, len(rows))

# Background task
def long_task():
    time.sleep(5)
    
thread = run_in_thread(long_task)
```

---

## Summary Table

| Module | Exports | Primary Use |
|--------|---------|-------------|
| C14 | 13 | Snowflake SSO, SQL execution, DataFrames |
| C15 | 7 | Local file caching (JSON, CSV, pickle) |
| C16 | 3 | Parallel/batch task execution |
| C17 | 4 | REST API requests with retry |
| C18 | 5 | Selenium browser automation |
| C19 | 12 | Google Drive detection and API |
| C20 | 6 | GUI popups, progress, threading |

**Total: 50 exports**

> *Export counts are indicative. `__all__` in each module's source code is authoritative.*