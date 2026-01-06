# A04 — Anti-Pattern Reference

> **What NOT to write.** Comprehensive list of patterns that indicate Core functions should be used.

**Status:** ✅ Complete — All C00-C20 modules validated

---

## Review Progress

| Module | Status | Notes |
|--------|--------|-------|
| C00_set_packages | ✅ Complete | Simplified to one rule + exception + reference list |
| C01_logging_handler | ✅ Complete | Validated + expanded with level imports, handlers, dividers |
| C02_set_file_paths | ✅ Complete | Validated + expanded with all 15 directory constants, temp files, path safety |
| C03_system_processes | ✅ Complete | Validated + expanded with WSL, iOS, platform-conditional patterns |
| C04_config_loader | ✅ Complete | Validated + expanded with file loaders, CONFIG access, merge_dicts |
| C05_error_handler | ✅ Complete | Validated + expanded with exception hooks, fatal patterns |
| C06_validation_utils | ✅ Complete | Validated — file/dir checks, DataFrame validation, config validation |
| C07_datetime_utils | ✅ Complete | Validated + expanded with week/month helpers, parsing, reporting |
| C08_string_utils | ✅ Complete | Validated — text normalisation, slugify, IDs, parse_number, dated filenames |
| C09_io_utils | ✅ Complete | Validated — CSV, JSON, Excel, file search, append (no read_excel) |
| C10_pdf_utils | ✅ Complete | Validated — text extraction, manipulation, tables, field extraction, validation |
| C11_file_backup | ✅ Complete | Validated — backup creation, zipped backups, listing, purge, restore |
| C12_data_processing | ✅ Complete | Validated — column standardisation, datetime, fill, dedup, merge, filter |
| C13_data_audit | ✅ Complete | Validated — missing rows, DataFrame comparison, sum reconciliation, audit summaries |
| C14_snowflake_connector | ✅ Complete | Validated — connection, context, SQL execution, SQL file loading, DataFrame results |
| C15_cache_manager | ✅ Complete | Validated — save/load cache (JSON, CSV, pickle), clear, list |
| C16_parallel_executor | ✅ Complete | Validated — run_in_parallel, chunk_tasks, run_batches |
| C17_api_manager | ✅ Complete | Validated — api_request, get_json, post_json, get_auth_header |
| C18_web_automation | ✅ Complete | Validated — get_chrome_driver, wait_for_element, scroll_to_bottom, click_element, close_driver |
| C19_google_drive_integration | ✅ Complete | Validated — local drive detection, API auth, find/upload/download |
| C20_gui_helpers | ✅ Complete | Validated — show_info/warning/error, ProgressPopup, run_in_thread, GUI_THEME |

---

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **CRITICAL** | Architectural violation — breaks framework guarantees | Must fix before delivery |
| **MAJOR** | Reimplemented Core functionality — creates drift | Must fix before delivery |
| **MINOR** | Style/preference — Core way is better but not required | Fix if time permits |

---

## C00 — Direct Package Imports (CRITICAL) ✅

**Rule:** ALL external and standard library packages MUST come from `C00_set_packages`. No exceptions.

### The One Rule

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Any `import <package>` statement | CRITICAL | `from core.C00_set_packages import *` |
| Any `from <package> import` statement | CRITICAL | `from core.C00_set_packages import *` |

### Exception

**Section 1 bootstrap ONLY** — these two imports are permitted at the top of every module:
```python
import sys
from pathlib import Path
```

This is required to set up `sys.path` before C00 can be imported.

### Detection Examples

```python
# ❌ WRONG - Direct imports
import pandas as pd
import numpy as np
import requests
import json
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

# ✅ CORRECT - Single import from C00
from core.C00_set_packages import *
# Now pd, np, requests, json, datetime, Dict, List, etc. are all available
```

### What C00 Provides

C00 exports 60+ symbols including:
- **Aliases:** `pd` (pandas), `np` (numpy), `dt` (datetime module)
- **Standard library:** `json`, `csv`, `yaml`, `re`, `os`, `shutil`, `glob`, `tempfile`, `subprocess`, `hashlib`, `pickle`, `zipfile`, `time`, `threading`, `queue`, `platform`, `getpass`, `logging`, `calendar`, `io`, `contextlib`
- **Datetime:** `datetime`, `date`, `timedelta`, `dt`
- **Typing:** `Any`, `Dict`, `List`, `Optional`, `Tuple`, `Union`, `Callable`, `Literal`, `Type`, `Sequence`, `Mapping`, `Protocol`, `TYPE_CHECKING`, `cast`, `overload`
- **Utilities:** `Path`, `deepcopy`, `dedent`, `dataclass`, `BytesIO`
- **Concurrency:** `ThreadPoolExecutor`, `ProcessPoolExecutor`, `as_completed`
- **Third-party:** `requests`, `tqdm`, `openpyxl`, `pdfplumber`, `PyPDF2`, `extract_text`, `snowflake`
- **Selenium:** `webdriver`, `By`, `Keys`, `Options`, `WebDriverWait`, `EC`, `ChromeDriverManager`
- **Google API:** `Credentials`, `InstalledAppFlow`, `build`, `HttpError`, `MediaFileUpload`, `MediaIoBaseDownload`, `Request`

---

## C01 — Logging Violations (CRITICAL/MAJOR) ✅

**Rule:** Use centralised logging, never print(). Import logging levels from C01.

### Direct Print / Output Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `print(` | CRITICAL | `logger.info()`, `logger.debug()`, `logger.warning()` |
| `sys.stdout.write(` | MAJOR | `logger.info()` |
| `sys.stderr.write(` | MAJOR | `logger.error()` |

### Logging Configuration Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `logging.basicConfig(` | MAJOR | `init_logging()` from C01 |
| `logging.FileHandler(` | MAJOR | `init_logging()` from C01 (handles file logging) |
| `logging.StreamHandler(` | MAJOR | `init_logging(enable_console=True)` from C01 |
| `logging.Formatter(` | MAJOR | `init_logging()` from C01 (uses `LOG_FORMAT`, `DATE_FORMAT`) |
| `logging.setLevel(` on root | MAJOR | `init_logging(level=...)` from C01 |

### Logger Instance Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `logging.getLogger(` | MAJOR | `get_logger(__name__)` from C01 |
| `logging.info(` / `logging.debug(` etc. | MAJOR | `logger = get_logger(__name__)` then `logger.info()` |

### Logging Level Import Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `from logging import DEBUG` | CRITICAL | `from core.C01_logging_handler import DEBUG` |
| `from logging import INFO` | CRITICAL | `from core.C01_logging_handler import INFO` |
| `from logging import WARNING` | CRITICAL | `from core.C01_logging_handler import WARNING` |
| `from logging import ERROR` | CRITICAL | `from core.C01_logging_handler import ERROR` |
| `from logging import CRITICAL` | CRITICAL | `from core.C01_logging_handler import CRITICAL` |
| `logging.DEBUG` / `logging.INFO` etc. | MAJOR | Use `DEBUG`, `INFO` etc. from C01 |

### Exception Logging Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `except Exception as e:` without `log_exception` | MAJOR | `log_exception(e, context="...")` from C01 |
| `except:` (bare except) | MAJOR | `except Exception as e: log_exception(e, ...)` |
| `traceback.print_exc()` | MAJOR | `log_exception(e, ...)` from C01 |
| `traceback.format_exc()` for logging | MAJOR | `log_exception(e, ...)` from C01 |
| `logger.exception(` without context | MINOR | `log_exception(e, context="...")` for consistency |

### Log Formatting Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual `"=" * 80` or `"-" * 80` dividers | MINOR | `log_divider(label="...")` from C01 |
| Custom log separator formatting | MINOR | `log_divider(level="info", label="...", width=80)` from C01 |

**Available Constants:** `LOG_FORMAT`, `DATE_FORMAT`, `LOGS_DIR`, `active_log_file`

---

## C02 — Path Violations (CRITICAL/MAJOR) ✅

**Rule:** Use C02 constants and utilities for all path operations. Never hardcode directory paths.

### Project Root Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `Path(__file__).resolve().parent.parent` | CRITICAL | `PROJECT_ROOT` from C02 |
| `Path(__file__).parent.parent` | CRITICAL | `PROJECT_ROOT` from C02 |
| `os.path.dirname(os.path.dirname(` | CRITICAL | `PROJECT_ROOT` from C02 |
| `str(PROJECT_ROOT)` | MINOR | `PROJECT_ROOT_STR` from C02 |
| `PROJECT_ROOT.name` | MINOR | `PROJECT_NAME` from C02 |
| `Path.home()` | MINOR | `USER_HOME_DIR` from C02 |

### Directory Creation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `os.makedirs(path, exist_ok=True)` | MAJOR | `ensure_directory(path)` from C02 |
| `Path(path).mkdir(parents=True, exist_ok=True)` | MAJOR | `ensure_directory(path)` from C02 |
| `os.mkdir(` | MAJOR | `ensure_directory(path)` from C02 |
| `path.mkdir(` | MAJOR | `ensure_directory(path)` from C02 |

### Path Building Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `os.path.join(` | MINOR | `build_path()` from C02 or `/` operator |
| `Path(*parts)` without resolve | MINOR | `build_path(*parts)` from C02 (auto-resolves) |

### Hardcoded Directory Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Hardcoded `"/data/"` or `"data/"` | MAJOR | `DATA_DIR` from C02 |
| Hardcoded `"/outputs/"` or `"outputs/"` | MAJOR | `OUTPUTS_DIR` from C02 |
| Hardcoded `"/config/"` or `"config/"` | MAJOR | `CONFIG_DIR` from C02 |
| Hardcoded `"/logs/"` or `"logs/"` | MAJOR | `LOGS_DIR` from C02 |
| Hardcoded `"/cache/"` or `"cache/"` | MAJOR | `CACHE_DIR` from C02 |
| Hardcoded `"/core/"` or `"core/"` | MAJOR | `CORE_DIR` from C02 |
| Hardcoded `"/gui/"` or `"gui/"` | MAJOR | `GUI_DIR` from C02 |
| Hardcoded `"/credentials/"` | MAJOR | `CREDENTIALS_DIR` from C02 |
| Hardcoded `"/binary_files/"` | MAJOR | `BINARY_FILES_DIR` from C02 |
| Hardcoded `"/implementation/"` | MAJOR | `IMPLEMENTATION_DIR` from C02 |
| Hardcoded `"/main/"` | MAJOR | `MAIN_DIR` from C02 |
| Hardcoded `"/scratchpad/"` | MAJOR | `SCRATCHPAD_DIR` from C02 |
| Hardcoded `"/sql/"` | MAJOR | `SQL_DIR` from C02 |
| Hardcoded `"/tech_docs/"` | MAJOR | `TECH_DOCS_DIR` from C02 |
| Hardcoded `"/user_guides/"` | MAJOR | `USER_GUIDES_DIR` from C02 |

### Temporary File Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `tempfile.NamedTemporaryFile` | MINOR | `get_temp_file()` from C02 |
| `tempfile.mktemp` | MINOR | `get_temp_file()` from C02 |
| `tempfile.mkstemp(` | MINOR | `get_temp_file(suffix, prefix, directory)` from C02 |
| `tempfile.gettempdir()` | MINOR | `get_temp_file(directory=...)` from C02 |

### Path Existence Check Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `try: path.exists() except:` | MINOR | `path_exists_safely(path)` from C02 |
| Manual exception handling around path checks | MINOR | `path_exists_safely(path)` from C02 |

### Google Drive Credential Path Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Hardcoded `"credentials.json"` path | MAJOR | `GDRIVE_CREDENTIALS_FILE` from C02 |
| Hardcoded `"token.json"` path | MAJOR | `GDRIVE_TOKEN_FILE` from C02 |
| `CREDENTIALS_DIR / "credentials.json"` | MINOR | `GDRIVE_CREDENTIALS_FILE` from C02 |
| `CREDENTIALS_DIR / "token.json"` | MINOR | `GDRIVE_TOKEN_FILE` from C02 |

### Windows Shared Drive Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual "Shared drives" path parsing | MINOR | `normalise_shared_drive_root(path)` from C02 |
| Manual drive root extraction on Windows | MINOR | `normalise_shared_drive_root(path)` from C02 |

**Available Constants:**
- Root: `PROJECT_ROOT`, `PROJECT_ROOT_STR`, `PROJECT_NAME`, `USER_HOME_DIR`
- Directories: `DATA_DIR`, `OUTPUTS_DIR`, `CONFIG_DIR`, `LOGS_DIR`, `CACHE_DIR`, `CORE_DIR`, `GUI_DIR`, `CREDENTIALS_DIR`, `BINARY_FILES_DIR`, `IMPLEMENTATION_DIR`, `MAIN_DIR`, `SCRATCHPAD_DIR`, `SQL_DIR`, `TECH_DOCS_DIR`, `USER_GUIDES_DIR`
- Tuple: `CORE_FOLDERS` (all directory constants)
- Google: `GDRIVE_DIR`, `GDRIVE_CREDENTIALS_FILE`, `GDRIVE_TOKEN_FILE`

---

## C03 — System/OS Violations (MAJOR) ✅

**Rule:** Use C03 for OS detection and platform-specific paths. Never manually detect OS or construct platform-specific paths.

### OS Detection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `platform.system()` | MAJOR | `detect_os()` from C03 |
| `sys.platform` (for OS checks) | MAJOR | `detect_os()` from C03 |
| `os.name` | MAJOR | `detect_os()` from C03 |
| `platform.platform()` | MAJOR | `detect_os()` from C03 |
| `platform.uname()` for OS detection | MAJOR | `detect_os()` from C03 |
| `platform.machine()` for OS/device detection | MAJOR | `detect_os()` from C03 |
| Manual `if sys.platform == "win32":` | MAJOR | `if detect_os() == "Windows":` |
| Manual `if sys.platform == "darwin":` | MAJOR | `if detect_os() == "macOS":` |
| Manual `if sys.platform.startswith("linux"):` | MAJOR | `if detect_os() == "Linux":` |

### WSL Detection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `"microsoft" in platform.uname().release` | MAJOR | `detect_os()` from C03 (returns "Windows (WSL)") |
| `"wsl" in platform.uname().release` | MAJOR | `detect_os()` from C03 (returns "Windows (WSL)") |
| Manual WSL detection logic | MAJOR | `detect_os()` from C03 |
| `getpass.getuser()` for WSL username paths | MAJOR | `user_download_folder()` from C03 (handles internally) |

### iOS Detection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `platform.machine().startswith("iP")` | MAJOR | `detect_os()` from C03 (returns "iOS") |
| Manual iPhone/iPad detection | MAJOR | `detect_os()` from C03 |

### User Download Folder Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `Path.home() / "Downloads"` | MAJOR | `user_download_folder()` from C03 |
| `os.path.expanduser("~/Downloads")` | MAJOR | `user_download_folder()` from C03 |
| `os.path.join(os.path.expanduser("~"), "Downloads")` | MAJOR | `user_download_folder()` from C03 |
| `/mnt/c/Users/` hardcoded paths | MAJOR | `user_download_folder()` from C03 |
| `Path(f"/mnt/c/Users/{user}/Downloads")` | MAJOR | `user_download_folder()` from C03 |

### Platform-Conditional Code Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `if os.name == "nt":` | MAJOR | `if detect_os() == "Windows":` |
| `if os.name == "posix":` | MAJOR | `if detect_os() in ("Linux", "macOS"):` |

**Available Functions:** `detect_os()`, `user_download_folder()`

**Return Values for `detect_os()`:** `"Windows"`, `"Windows (WSL)"`, `"macOS"`, `"Linux"`, `"iOS"`

---

## C04 — Config Violations (MAJOR) ✅

**Rule:** Use C04 for configuration loading. Never manually load config files or access CONFIG without initialisation.

### Direct Config File Loading Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `yaml.safe_load(open('config.yaml'))` | MAJOR | `initialise_config()` + `get_config()` from C04 |
| `yaml.safe_load(open('config.yml'))` | MAJOR | `initialise_config()` + `get_config()` from C04 |
| `yaml.load(` | MAJOR | `initialise_config()` + `get_config()` from C04 |
| `json.load(open('settings.json'))` | MAJOR | `initialise_config()` + `get_config()` from C04 |
| `json.load(open('config.json'))` | MAJOR | `initialise_config()` + `get_config()` from C04 |

### Config File Path Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `with open('config/` | MAJOR | Use C04 functions (auto-discovers config files) |
| `with open(CONFIG_DIR /` for config | MAJOR | Use `load_yaml_config()` or `load_json_config()` from C04 |
| Hardcoded `"config.yaml"` path | MAJOR | `initialise_config()` from C04 (auto-discovers) |
| Hardcoded `"config.yml"` path | MAJOR | `initialise_config()` from C04 (auto-discovers) |
| Hardcoded `"settings.json"` path | MAJOR | `initialise_config()` from C04 (auto-discovers) |
| `Path("config/config.yaml")` | MAJOR | `initialise_config()` from C04 |

### CONFIG Access Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `CONFIG[section][key]` without initialise | MAJOR | Call `initialise_config()` first, then `get_config()` |
| `CONFIG.get(section, {}).get(key)` | MAJOR | `get_config(section, key, default)` from C04 |
| Direct `CONFIG["section"]["key"]` | MAJOR | `get_config("section", "key")` from C04 (handles missing keys) |
| Accessing `CONFIG` before `initialise_config()` | MAJOR | Always call `initialise_config()` first |

### Dictionary Merging Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual recursive dict merging | MINOR | `merge_dicts(base, update)` from C04 |
| `{**dict1, **dict2}` for nested config | MINOR | `merge_dicts(base, update)` from C04 (recursive) |
| `dict1.update(dict2)` for nested config | MINOR | `merge_dicts(base, update)` from C04 (recursive) |

### Standalone Config File Loading

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `yaml.safe_load(path.read_text())` for config | MINOR | `load_yaml_config(path)` from C04 |
| `json.loads(path.read_text())` for config | MINOR | `load_json_config(path)` from C04 |
| Manual error handling around config loading | MINOR | `load_yaml_config()` / `load_json_config()` (handles errors) |

**Available Functions:**
- State: `CONFIG`, `DEFAULT_FILES`
- Loaders: `load_yaml_config(path)`, `load_json_config(path)`
- Utilities: `merge_dicts(base, update)`
- Management: `initialise_config()`, `reload_config()`, `get_config(section, key, default=None)`

**Typical Usage Pattern:**
```python
from core.C04_config_loader import initialise_config, get_config

initialise_config()  # Must call before accessing config
db_user = get_config("snowflake", "user")
```

---

## C05 — Error Handling Violations (MAJOR) ✅

**Rule:** Use C05 for centralised error handling. Never use `sys.exit()` directly or manually set exception hooks.

### Fatal Exit Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `sys.exit(1)` | MAJOR | `handle_error(exception, fatal=True)` from C05 |
| `sys.exit(0)` for error cases | MAJOR | `handle_error(exception, fatal=True)` from C05 |
| `raise SystemExit(1)` | MAJOR | `handle_error(exception, fatal=True)` from C05 |
| `raise SystemExit(` | MAJOR | `handle_error(exception, fatal=True)` from C05 |
| `exit(1)` | MAJOR | `handle_error(exception, fatal=True)` from C05 |
| `quit()` | MAJOR | `handle_error(exception, fatal=True)` from C05 |

### Exception Hook Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `sys.excepthook = ` | MAJOR | `install_global_exception_hook()` from C05 |
| Manual global exception handler | MAJOR | `install_global_exception_hook()` from C05 |
| `sys.__excepthook__` (except in C05) | MAJOR | `install_global_exception_hook()` from C05 |

### Exception Handling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `except Exception as e:` with manual logging + exit | MAJOR | `handle_error(e, context="...", fatal=True)` from C05 |
| `except Exception as e: logger.error(...); sys.exit(1)` | MAJOR | `handle_error(e, context="...", fatal=True)` from C05 |
| Manual "log then exit" pattern | MAJOR | `handle_error(e, fatal=True)` from C05 |

### Context-Free Error Handling

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `handle_error(e)` without context | MINOR | `handle_error(e, context="descriptive context")` |
| Exception handling without context info | MINOR | Always provide `context=` parameter |

**Available Functions:**
- `handle_error(exception, context="", fatal=False)` — Log exception, optionally exit
- `install_global_exception_hook()` — Install global uncaught exception handler
- `global_exception_hook(exc_type, exc_value, exc_traceback)` — The hook itself (rarely called directly)
- `simulate_error()` — Test utility (raises ValueError)

**Configuration:** Respects `CONFIG["error_handling"]["exit_on_fatal"]` to control fatal behaviour.

---

## C06 — Validation Violations (MAJOR) ✅

**Rule:** Use C06 for all validation checks — file/directory existence, DataFrame validation, and config validation. C06 provides both raising validators and boolean convenience functions.

### File Existence Check Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `os.path.exists(path)` | MAJOR | `file_exists(path)` from C06 (returns bool) |
| `os.path.isfile(path)` | MAJOR | `file_exists(path)` from C06 |
| `Path(x).exists()` | MAJOR | `file_exists(path)` from C06 |
| `Path(x).is_file()` | MAJOR | `file_exists(path)` from C06 |
| `if not path.exists(): raise` | MAJOR | `validate_file_exists(path)` from C06 (raises FileNotFoundError) |

### Directory Existence Check Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `os.path.isdir(path)` | MAJOR | `dir_exists(path)` from C06 (returns bool) |
| `Path(x).is_dir()` | MAJOR | `dir_exists(path)` from C06 |
| `if not path.is_dir(): raise` | MAJOR | `validate_directory_exists(path)` from C06 (raises FileNotFoundError) |
| `if not path.exists(): path.mkdir(...)` | MAJOR | `validate_directory_exists(path, create_if_missing=True)` from C06 |

### DataFrame Column Validation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `if col not in df.columns: raise` | MAJOR | `validate_required_columns(df, [col, ...])` from C06 |
| `missing = [c for c in cols if c not in df.columns]` | MAJOR | `validate_required_columns(df, cols)` from C06 |
| `set(required) - set(df.columns)` | MAJOR | `validate_required_columns(df, required)` from C06 |
| Manual column presence check loop | MAJOR | `validate_required_columns(df, cols)` from C06 |

### DataFrame Empty Check Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `if df.empty: raise` | MAJOR | `validate_non_empty(df, label="...")` from C06 |
| `if len(df) == 0: raise` | MAJOR | `validate_non_empty(df, label="...")` from C06 |
| `if data is None or len(data) == 0:` | MAJOR | `validate_non_empty(data, label="...")` from C06 |

### Numeric Column Validation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `if not pd.api.types.is_numeric_dtype(df[col]):` | MAJOR | `validate_numeric(df, column)` from C06 |
| `df[col].dtype` checks for numeric | MAJOR | `validate_numeric(df, column)` from C06 |
| Manual numeric type validation | MAJOR | `validate_numeric(df, column)` from C06 |

### Config Key Validation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual loop checking config keys exist | MAJOR | `validate_config_keys(section, keys)` from C06 |
| `if get_config(section, key) is None: raise` | MAJOR | `validate_config_keys(section, [key, ...])` from C06 |
| Multiple `get_config()` calls with existence checks | MINOR | `validate_config_keys(section, keys)` from C06 |

### Validation Reporting Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual logging of validation pass/fail summary | MINOR | `validation_report(results_dict)` from C06 |

**Available Functions:**
- **File/Dir (raising):** `validate_file_exists(path)`, `validate_directory_exists(path, create_if_missing=False)`
- **File/Dir (bool):** `file_exists(path)`, `dir_exists(path)`
- **DataFrame:** `validate_required_columns(df, cols)`, `validate_non_empty(data, label)`, `validate_numeric(df, column)`
- **Config:** `validate_config_keys(section, keys)`
- **Reporting:** `validation_report(results_dict)`

---

## C07 — Date/Time Violations (MAJOR) ✅

**Rule:** Use C07 for all date/time operations. Never use raw datetime methods directly.

### Current Date/Time Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `datetime.now()` | MAJOR | `get_now()` from C07 |
| `datetime.today()` | MAJOR | `get_now()` from C07 |
| `date.today()` | MAJOR | `get_today()` from C07 |

### Date Formatting Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `.strftime("%Y-%m-%d")` | MAJOR | `as_str(d)` from C07 |
| `.strftime(` for any format | MAJOR | `format_date(d, fmt)` from C07 |
| `datetime.now().strftime("%Y%m%d_%H%M%S")` | MAJOR | `timestamp_now()` from C07 |
| `f"{d:%Y-%m-%d}"` formatting | MINOR | `as_str(d)` or `format_date(d, fmt)` from C07 |

### Date Parsing Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `datetime.strptime(` | MAJOR | `parse_date(value, fmt)` from C07 |
| `datetime.strptime(...).date()` | MAJOR | `parse_date(value, fmt)` from C07 |
| Manual multi-format date parsing loop | MAJOR | `parse_date(value, fmt=None)` from C07 (auto-detects) |
| `try: strptime(...) except: return None` | MAJOR | `try_parse_date(value, fmt)` from C07 |

### Week Boundary Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `d - timedelta(days=d.weekday())` | MAJOR | `get_start_of_week(d)` from C07 |
| Manual Monday calculation | MAJOR | `get_start_of_week(d)` from C07 |
| Manual Sunday calculation | MAJOR | `get_end_of_week(d)` from C07 |
| `(get_start_of_week(d), get_end_of_week(d))` | MINOR | `get_week_range(d)` from C07 |
| `d.isocalendar()` for week ID | MINOR | `get_week_id(d)` from C07 |

### Month Boundary Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `d.replace(day=1)` | MAJOR | `get_start_of_month(d)` from C07 |
| `calendar.monthrange(year, month)` | MAJOR | `get_end_of_month(d)` or `get_month_range(year, month)` from C07 |
| Manual last-day-of-month calculation | MAJOR | `get_end_of_month(d)` from C07 |
| Manual previous month calculation | MAJOR | `get_previous_month(d, fmt)` from C07 |

### Date Range Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `[start + timedelta(days=i) for i in range(...)]` | MAJOR | `generate_date_range(start, end)` from C07 |
| Manual date iteration loop | MAJOR | `generate_date_range(start, end)` from C07 |
| `start <= d <= end` for range check | MINOR | `is_within_range(d, start, end)` from C07 |

### Fiscal/Reporting Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `(month - 1) // 3 + 1` for quarter | MAJOR | `get_fiscal_quarter(d)` from C07 |
| Manual quarter calculation | MAJOR | `get_fiscal_quarter(d)` from C07 |
| Manual ISO week string formatting | MINOR | `get_week_id(d)` from C07 |

**Available Functions:**
- **Constants:** `DEFAULT_DATE_FORMAT` (`"%Y-%m-%d"`)
- **Formatting:** `as_str(d)`, `timestamp_now(fmt)`, `format_date(d, fmt)`
- **Basic:** `get_today()`, `get_now()`, `parse_date(value, fmt)`, `try_parse_date(value, fmt)`
- **Week:** `get_start_of_week(d)`, `get_end_of_week(d)`, `get_week_range(d)`
- **Month:** `get_start_of_month(d)`, `get_end_of_month(d)`, `get_month_range(year, month)`, `get_previous_month(d, fmt)`
- **Range:** `generate_date_range(start, end)`, `is_within_range(d, start, end)`
- **Reporting:** `get_fiscal_quarter(d)`, `get_week_id(d)`

---

## C08 — String Utilities Violations (MINOR) ✅

**Rule:** Use C08 for common string operations like text normalisation, filename cleaning, pattern extraction, and number parsing. Available via `StringUtils` class or standalone functions.

### Text Normalisation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `text.lower().strip()` | MINOR | `normalize_text(text)` from C08 |
| `unicodedata.normalize("NFKD", text)` | MINOR | `normalize_text(text)` from C08 |
| `re.sub(r"\s+", " ", text)` for whitespace collapse | MINOR | `normalize_text(text)` from C08 |
| Manual accent/diacritic removal | MINOR | `normalize_text(text)` from C08 |

### Filename Cleaning Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `re.sub(r"[^a-z0-9]+", "_", name)` | MINOR | `slugify_filename(filename)` from C08 |
| Manual unsafe character replacement | MINOR | `slugify_filename(filename)` from C08 |
| `os.path.splitext()` + manual cleaning | MINOR | `slugify_filename(filename, keep_extension=True)` from C08 |
| Complex filename sanitisation logic | MINOR | `clean_filename_generic(original_name)` from C08 |

### ID Generation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual slug/ID generation from text | MINOR | `make_safe_id(text, max_length=50)` from C08 |
| `text.replace(" ", "_").lower()[:50]` | MINOR | `make_safe_id(text, max_length)` from C08 |

### Pattern Extraction Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `re.search(pattern, text).group(0)` without None check | MINOR | `extract_pattern(text, pattern, group)` from C08 |
| Manual regex extraction with try/except | MINOR | `extract_pattern(text, pattern, group)` from C08 |

### Number Parsing Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `float(text.replace(",", ""))` | MINOR | `parse_number(value)` from C08 |
| Manual currency symbol removal (`£`, `GBP`) | MINOR | `parse_number(value)` from C08 |
| Manual parenthesis-to-negative conversion | MINOR | `parse_number(value)` from C08 |
| Complex string-to-float with error handling | MINOR | `parse_number(value)` from C08 |

### Dated Filename Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `f"{date:%y.%m.%d} - {name}.csv"` | MINOR | `generate_dated_filename(descriptor, extension, ...)` from C08 |
| Manual date-prefixed filename construction | MINOR | `generate_dated_filename(...)` from C08 |
| `f"{today.strftime('%Y%m%d')}_{filename}"` | MINOR | `generate_dated_filename(...)` from C08 |

**Available Functions:**
- **Class:** `StringUtils` (namespace with static methods)
- **Text:** `normalize_text(text)` — lowercase, accent-free, whitespace-collapsed
- **Filenames:** `slugify_filename(filename, keep_extension=True)`, `clean_filename_generic(original_name)`, `generate_dated_filename(descriptor, extension, start_date, end_date, frequency)`
- **IDs:** `make_safe_id(text, max_length=50)`
- **Extraction:** `extract_pattern(text, pattern, group)`
- **Numbers:** `parse_number(value)` — handles currency, commas, parentheses for negatives

---

## C09 — Data I/O Violations (MAJOR) ✅

**Rule:** Use C09 for reading/writing data files (CSV, JSON, Excel). Never use raw pandas or json methods directly.

### CSV Read Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pd.read_csv(` | MAJOR | `read_csv_file(path, **kwargs)` from C09 |
| `pandas.read_csv(` | MAJOR | `read_csv_file(path, **kwargs)` from C09 |

### CSV/DataFrame Write Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.to_csv(` | MAJOR | `save_dataframe(df, path, ...)` from C09 |
| `DataFrame.to_csv(` | MAJOR | `save_dataframe(df, path, ...)` from C09 |
| Manual backup before CSV overwrite | MINOR | `save_dataframe(..., backup_existing=True)` from C09 |
| Manual timestamped filename for versioning | MINOR | `save_dataframe(..., overwrite=False)` from C09 |

### JSON Read Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `json.load(` | MAJOR | `read_json(path)` from C09 |
| `with open(path) as f: json.load(f)` | MAJOR | `read_json(path)` from C09 |
| `json.loads(path.read_text())` | MAJOR | `read_json(path)` from C09 |

### JSON Write Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `json.dump(` | MAJOR | `save_json(data, path, ...)` from C09 |
| `with open(path, "w") as f: json.dump(...)` | MAJOR | `save_json(data, path, indent=4)` from C09 |
| `path.write_text(json.dumps(...))` | MAJOR | `save_json(data, path)` from C09 |

### Excel Write Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.to_excel(` | MAJOR | `save_excel(df, path, sheet_name, ...)` from C09 |
| `DataFrame.to_excel(` | MAJOR | `save_excel(df, path, ...)` from C09 |
| `pd.ExcelWriter(` | MAJOR | `save_excel(df, path, ...)` from C09 |

### File Search Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `max(path.glob("*.csv"), key=lambda f: f.stat().st_mtime)` | MAJOR | `get_latest_file(directory, pattern)` from C09 |
| `sorted(path.glob(...), key=os.path.getmtime)[-1]` | MAJOR | `get_latest_file(directory, pattern)` from C09 |
| Manual "find newest file" logic | MAJOR | `get_latest_file(directory, pattern)` from C09 |

### Text Append Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `with open(path, "a") as f: f.write(...)` | MINOR | `append_to_file(path, text, newline=True)` from C09 |
| Manual append mode file writing | MINOR | `append_to_file(path, text)` from C09 |

**Available Functions:**
- **CSV:** `read_csv_file(path, **kwargs)`, `save_dataframe(df, path, overwrite=True, backup_existing=True, index=False, **kwargs)`
- **JSON:** `read_json(path, encoding="utf-8")`, `save_json(data, path, indent=4, overwrite=True, encoding="utf-8")`
- **Excel:** `save_excel(df, path, sheet_name="Sheet1", index=False, **kwargs)`
- **Utilities:** `get_latest_file(directory, pattern="*")`, `append_to_file(path, text, newline=True)`

**Note:** C09 does NOT provide `read_excel()` — use `pd.read_excel()` via C00 for now, or check if C11 has Excel-specific utilities.

---

## C10 — PDF Violations (MAJOR) ✅

**Rule:** Use C10 for all PDF operations. Never use pdfplumber, PyPDF2, or pdfminer directly. Available via `PDFUtils` class or standalone functions.

### PDF Text Extraction Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pdfplumber.open(` | MAJOR | `extract_pdf_text(path)` from C10 |
| `with pdfplumber.open(...) as pdf:` | MAJOR | `extract_pdf_text(path)` from C10 |
| `pdf.pages[n].extract_text()` | MAJOR | `extract_pdf_text_by_page(path, page_num)` from C10 |
| `extract_text(` from pdfminer | MAJOR | `extract_pdf_text(path)` from C10 |

### PDF Reading/Page Count Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `PdfReader(` | MAJOR | `get_pdf_page_count(path)` or other C10 functions |
| `PyPDF2.PdfReader(` | MAJOR | Use C10 functions instead |
| `len(reader.pages)` | MAJOR | `get_pdf_page_count(path)` from C10 |

### PDF Manipulation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `PdfWriter(` | MAJOR | `merge_pdfs()`, `extract_pages()`, `rotate_pdf()` from C10 |
| `PyPDF2.PdfWriter(` | MAJOR | Use C10 manipulation functions |
| `page.rotate(` | MAJOR | `rotate_pdf(path, angle)` from C10 |
| `writer.add_page(` | MAJOR | `merge_pdfs(paths)` or `extract_pages(path, pages)` from C10 |
| `PdfMerger(` | MAJOR | `merge_pdfs(paths, output_path)` from C10 |

### PDF Field/Pattern Extraction Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `re.search(pattern, pdf_text)` for invoice fields | MINOR | `extract_field(text, pattern, flags, group)` from C10 |
| `re.findall(pattern, pdf_text)` for multiple matches | MINOR | `extract_all_fields(text, pattern, flags, group)` from C10 |
| Manual regex extraction from PDF text | MINOR | `extract_field()` or `extract_all_fields()` from C10 |

### PDF Table Extraction Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `page.extract_tables()` | MAJOR | `extract_tables(path, page_num)` from C10 |
| `pdfplumber` table extraction | MAJOR | `extract_tables_to_dataframe(path, page_num)` from C10 |
| Manual PDF table to DataFrame conversion | MAJOR | `extract_tables_to_dataframe(path)` from C10 |

### PDF Validation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual PDF header validation (`%PDF-`) | MINOR | `is_valid_pdf(path)` from C10 |
| `try: PdfReader(...) except:` for validation | MINOR | `is_valid_pdf(path)` from C10 |

**Available Functions:**
- **Class:** `PDFUtils` (namespace with static methods)
- **Text Extraction:** `extract_pdf_text(path)`, `extract_pdf_text_by_page(path, page_num)`, `get_pdf_page_count(path)`
- **Field Extraction:** `extract_field(text, pattern, flags, group)`, `extract_all_fields(text, pattern, flags, group)`
- **Manipulation:** `rotate_pdf(path, angle)`, `merge_pdfs(paths, output_path)`, `extract_pages(path, page_numbers, output_path)`, `extract_pages_matching(path, pattern, flags)`, `remove_pages_containing(path, search_text, output_path)`
- **Tables:** `extract_tables(path, page_num)`, `extract_tables_to_dataframe(path, page_num)`
- **Validation:** `is_valid_pdf(path)`

---

## C11 — File Backup Violations (MAJOR) ✅

**Rule:** Use C11 for all backup operations. Never manually copy files with timestamps or create zip backups directly.

### Backup Creation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `shutil.copy2(file, f"{timestamp}_{file.name}")` | MAJOR | `create_backup(file_path)` from C11 |
| Manual timestamped file copy | MAJOR | `create_backup(file_path)` from C11 |
| `f"{timestamp_now()}_{filename}"` for backup naming | MAJOR | `create_backup(file_path)` from C11 |

### Compressed Backup Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `zipfile.ZipFile(path, "w")` for backup | MAJOR | `create_zipped_backup(file_path)` from C11 |
| `with zipfile.ZipFile(...) as zf: zf.write(...)` | MAJOR | `create_zipped_backup(file_path)` from C11 |
| Manual ZIP backup creation | MAJOR | `create_zipped_backup(file_path)` from C11 |

### Backup Listing Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `sorted(backup_dir.glob("*filename*"), key=...)` | MAJOR | `list_backups(original_filename)` from C11 |
| Manual backup file enumeration | MAJOR | `list_backups(original_filename)` from C11 |

### Backup Retention/Purge Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual deletion of old backup files | MAJOR | `purge_old_backups(filename, keep_latest=3)` from C11 |
| `backups[keep_count:].unlink()` patterns | MAJOR | `purge_old_backups(filename, keep_latest)` from C11 |

### Restore Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `shutil.copy2(backup_file, original_path)` for restore | MAJOR | `restore_backup(original_path, backup_file)` from C11 |
| `zipfile.ZipFile(backup).extract(...)` for restore | MAJOR | `restore_backup(original_path, backup_file)` from C11 |
| Manual backup restoration logic | MAJOR | `restore_backup(original_path, backup_file)` from C11 |

### MD5 Hashing Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `hashlib.md5()` with manual file chunking | MINOR | `compute_md5(file_path)` from C11 |
| Manual MD5 hash computation | MINOR | `compute_md5(file_path)` from C11 |

**Available Functions:**
- **Constants:** `BACKUP_DIR` (project backups directory)
- **Backup Creation:** `create_backup(file_path)`, `create_zipped_backup(file_path)`
- **Listing/Retention:** `list_backups(original_filename)`, `purge_old_backups(original_filename, keep_latest=3)`
- **Restore:** `restore_backup(original_path, backup_file)`
- **Utilities:** `compute_md5(file_path)`, `ensure_backup_dir()`

**Note:** All backups include companion `.json` metadata files with original path, timestamp, size, and MD5 hash.

---

## C12 — Data Processing Violations (MINOR) ✅

**Rule:** Use C12 for common DataFrame transformations. These provide consistent logging and standardised preprocessing.

### Column Standardisation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.columns = df.columns.str.lower()` | MINOR | `standardise_columns(df)` from C12 |
| `df.columns.str.strip().str.lower().str.replace(" ", "_")` | MINOR | `standardise_columns(df)` from C12 |
| `df.rename(columns=lambda c: c.lower().replace(" ", "_"))` | MINOR | `standardise_columns(df)` from C12 |

### Datetime Conversion Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pd.to_datetime(df[col], errors="coerce")` | MINOR | `convert_to_datetime(df, [col, ...])` from C12 |
| Manual datetime conversion loop over columns | MINOR | `convert_to_datetime(df, cols)` from C12 |

### Missing Value Handling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.fillna({"col1": 0, "col2": ""})` | MINOR | `fill_missing(df, fill_map)` from C12 |
| `df[col].fillna(value)` for multiple columns | MINOR | `fill_missing(df, {col: value, ...})` from C12 |

### Duplicate Removal Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.drop_duplicates(subset=[...])` | MINOR | `remove_duplicates(df, subset=[...])` from C12 |
| `df.drop_duplicates().reset_index(drop=True)` | MINOR | `remove_duplicates(df)` from C12 |

### Row Filtering Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df[df["col"] > value]` | MINOR | `filter_rows(df, lambda d: d["col"] > value)` from C12 |
| `df.loc[mask]` with complex conditions | MINOR | `filter_rows(df, condition)` from C12 |

### DataFrame Merge Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pd.merge(df1, df2, on=..., how=...)` | MINOR | `merge_dataframes(df1, df2, on, how)` from C12 |
| `df1.merge(df2, on=..., how=...)` | MINOR | `merge_dataframes(df1, df2, on, how)` from C12 |

### Summary Statistics Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df.describe(include=[np.number]).T` | MINOR | `summarise_numeric(df)` from C12 |
| Manual numeric column summary | MINOR | `summarise_numeric(df)` from C12 |

**Available Functions:**
- **Standardisation:** `standardise_columns(df)`, `convert_to_datetime(df, cols)`, `fill_missing(df, fill_map)`
- **Cleaning:** `remove_duplicates(df, subset=None)`, `filter_rows(df, condition)`
- **Merging/Summary:** `merge_dataframes(df1, df2, on, how="inner")`, `summarise_numeric(df)`

**Note:** C12 violations are MINOR because these are convenience wrappers that provide logging. Direct pandas operations work but miss audit trail benefits.

---

## C13 — Data Audit Violations (MINOR) ✅

**Rule:** Use C13 for DataFrame comparison, reconciliation, and audit workflows. These provide consistent logging and validation.

### Missing Row Detection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df_a[~df_a[key].isin(df_b[key])]` | MINOR | `get_missing_rows(df_a, df_b, on=key)` from C13 |
| Manual "rows in A not in B" logic | MINOR | `get_missing_rows(df_a, df_b, on)` from C13 |

### DataFrame Comparison Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pd.merge(df_a, df_b, ..., suffixes=("_a", "_b"))` for comparison | MINOR | `compare_dataframes(df_a, df_b, on, cols)` from C13 |
| Manual column-by-column mismatch detection | MINOR | `compare_dataframes(df_a, df_b, on, cols)` from C13 |
| `merged[merged[col_a] != merged[col_b]]` | MINOR | `compare_dataframes(df_a, df_b, on, cols)` from C13 |

### Sum Reconciliation Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `df_a[col].sum() - df_b[col].sum()` | MINOR | `reconcile_column_sums(df_a, df_b, column, ...)` from C13 |
| Manual variance calculation between DataFrames | MINOR | `reconcile_column_sums(df_a, df_b, column, label_a, label_b)` from C13 |
| Manual percentage difference calculation | MINOR | `reconcile_column_sums(...)` from C13 |

### Audit Summary Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `len(df_diffs)` + `df_diffs[key].nunique()` | MINOR | `summarise_differences(df_diffs, key_col)` from C13 |
| Manual mismatch counting and unique key counting | MINOR | `summarise_differences(df_diffs, key_col)` from C13 |
| Manual audit summary logging | MINOR | `log_audit_summary(source, target, missing, mismatches)` from C13 |

**Available Functions:**
- **Row Comparison:** `get_missing_rows(df_a, df_b, on)` — rows in df_a missing from df_b
- **Column Comparison:** `compare_dataframes(df_a, df_b, on, cols)` — find value mismatches
- **Sum Reconciliation:** `reconcile_column_sums(df_a, df_b, column, label_a, label_b)` — compare column totals with variance
- **Audit Summary:** `summarise_differences(df_diffs, key_col)`, `log_audit_summary(source_name, target_name, missing_count, mismatch_count)`

**Note:** C13 violations are MINOR because these are convenience wrappers for reconciliation workflows. Direct pandas operations work but miss audit trail benefits.

---

## C14 — Snowflake Violations (MAJOR) ✅

**Rule:** Use C14 for all Snowflake operations. Never use snowflake.connector directly.

### Connection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `snowflake.connector.connect(` | CRITICAL | `connect_to_snowflake(email)` from C14 |
| Manual Snowflake connection setup | CRITICAL | `connect_to_snowflake(email)` from C14 |
| `import snowflake.connector` | CRITICAL | Use C14 functions (snowflake is in C00) |
| Manual Okta/SSO authentication handling | MAJOR | `connect_to_snowflake(email)` from C14 |

### Context/Session Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `USE ROLE ...` / `USE WAREHOUSE ...` | MAJOR | `set_snowflake_context(conn, role, warehouse, ...)` from C14 |
| `USE DATABASE ...` / `USE SCHEMA ...` | MAJOR | `set_snowflake_context(conn, role, warehouse, database, schema)` from C14 |
| Manual role/warehouse selection | MAJOR | `connect_to_snowflake()` handles context automatically |

### SQL Execution Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `cursor.execute(sql)` | MAJOR | `run_query(conn, sql, fetch=True)` from C14 |
| `cursor.fetchall()` | MAJOR | `run_query(conn, sql, fetch=True)` from C14 |
| `cursor.fetchone()` | MAJOR | `run_query(conn, sql)` from C14 |
| Manual cursor handling for Snowflake | MAJOR | Use C14 functions |

### SQL File Loading Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `Path("sql/query.sql").read_text()` | MAJOR | `load_sql_file(filename, params)` from C14 |
| Manual SQL file reading | MAJOR | `load_sql_file(filename, params)` from C14 |
| `sql.format(**params)` for SQL templates | MINOR | `load_sql_file(filename, params)` from C14 |
| `run_query(conn, Path(...).read_text())` | MAJOR | `run_sql_file(conn, filename, params)` from C14 |

### DataFrame Results Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `pd.DataFrame(cursor.fetchall(), columns=...)` | MAJOR | `run_sql_to_dataframe(conn, sql)` from C14 |
| `cursor.fetch_pandas_all()` | MAJOR | `run_sql_to_dataframe(conn, sql)` from C14 |
| Manual DataFrame construction from Snowflake | MAJOR | `run_sql_to_dataframe(conn, sql, standardise=True)` from C14 |
| SQL file execution to DataFrame | MAJOR | `run_sql_file_to_dataframe(conn, filename, params)` from C14 |

**Available Functions:**
- **Constants:** `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_EMAIL_DOMAIN`, `CONTEXT_PRIORITY`, `DEFAULT_DATABASE`, `DEFAULT_SCHEMA`
- **Connection:** `get_snowflake_credentials(email)`, `set_snowflake_context(conn, role, warehouse, ...)`, `connect_to_snowflake(email)`
- **SQL Execution:** `run_query(conn, sql, fetch=True)`, `load_sql_file(filename, params)`, `run_sql_file(conn, filename, params, fetch=True)`
- **DataFrame Results:** `run_sql_to_dataframe(conn, sql, standardise=True)`, `run_sql_file_to_dataframe(conn, filename, params, standardise=True)`

**Note:** `connect_to_snowflake()` uses `print()` for interactive Okta prompts — this is an explicit exception to the "no print" rule.

---

## C15 — Cache Manager Violations (MINOR) ✅

**Rule:** Use C15 for caching frequently used data (API responses, DataFrames, query results). Supports JSON, CSV, and pickle formats.

### Cache Storage Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `json.dump(data, open("cache/..."))` | MINOR | `save_cache(name, data, fmt="json")` from C15 |
| `df.to_csv("cache/...")` for caching | MINOR | `save_cache(name, df, fmt="csv")` from C15 |
| `pickle.dump(obj, open("cache/..."))` | MINOR | `save_cache(name, obj, fmt="pkl")` from C15 |
| Manual cache file creation in `/cache/` | MINOR | `save_cache(name, data, fmt)` from C15 |

### Cache Loading Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `json.load(open("cache/..."))` | MINOR | `load_cache(name, fmt="json")` from C15 |
| `pd.read_csv("cache/...")` for cache | MINOR | `load_cache(name, fmt="csv")` from C15 |
| `pickle.load(open("cache/..."))` | MINOR | `load_cache(name, fmt="pkl")` from C15 |
| Manual cache file reading | MINOR | `load_cache(name, fmt)` from C15 |

### Cache Path Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `PROJECT_ROOT / "cache" / filename` | MINOR | `get_cache_path(name, fmt)` from C15 |
| Hardcoded cache directory paths | MINOR | Use `CACHE_DIR` from C15 |

### Cache Management Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `os.remove("cache/...")` | MINOR | `clear_cache(name)` from C15 |
| Manual cache file deletion | MINOR | `clear_cache(name)` or `clear_cache()` for all |
| `list(Path("cache").glob("*"))` | MINOR | `list_cache_files()` from C15 |

**Available Functions:**
- **Constants:** `CACHE_DIR` (project cache directory)
- **Path Building:** `get_cache_path(name, fmt="json")`, `ensure_cache_dir()`
- **Save/Load:** `save_cache(name, data, fmt="json")`, `load_cache(name, fmt="json")`
- **Management:** `clear_cache(name=None)` (None clears all), `list_cache_files()`

**Supported Formats:**
- `"json"` — Dictionary-like data
- `"csv"` — Pandas DataFrames
- `"pkl"` — Arbitrary Python objects (pickle)

**Note:** C15 violations are MINOR because manual caching works but misses consistent logging and path management.

---

## C16 — Parallel Processing Violations (MAJOR) ✅

**Rule:** Use C16 for all concurrent and parallel execution. Never use ThreadPoolExecutor or ProcessPoolExecutor directly.

### Executor Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `ThreadPoolExecutor(` | MAJOR | `run_in_parallel(func, tasks, mode="thread")` from C16 |
| `ProcessPoolExecutor(` | MAJOR | `run_in_parallel(func, tasks, mode="process")` from C16 |
| `with ThreadPoolExecutor(...) as executor:` | MAJOR | `run_in_parallel(func, tasks, mode="thread", max_workers=N)` from C16 |
| `with ProcessPoolExecutor(...) as executor:` | MAJOR | `run_in_parallel(func, tasks, mode="process", max_workers=N)` from C16 |

### Future Handling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `executor.submit(func, task)` | MAJOR | `run_in_parallel(func, [task, ...])` from C16 |
| `executor.map(func, tasks)` | MAJOR | `run_in_parallel(func, tasks)` from C16 |
| `as_completed(futures)` | MAJOR | `run_in_parallel(...)` from C16 (handles internally) |
| `future.result()` | MAJOR | `run_in_parallel(...)` from C16 (handles internally) |
| `concurrent.futures.wait(` | MAJOR | `run_in_parallel(...)` from C16 |

### Chunking/Batching Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `[items[i:i+n] for i in range(0, len(items), n)]` | MINOR | `chunk_tasks(task_list, chunk_size)` from C16 |
| Manual list chunking for batch processing | MINOR | `chunk_tasks(task_list, chunk_size)` from C16 |
| Manual batch execution with delays | MINOR | `run_batches(func, tasks, chunk_size, delay)` from C16 |
| `time.sleep(delay)` between batch iterations | MINOR | `run_batches(func, tasks, chunk_size, delay)` from C16 |

**Available Functions:**
- `run_in_parallel(func, tasks, mode="thread", max_workers=8, show_progress=True)` — Execute tasks concurrently
- `chunk_tasks(task_list, chunk_size)` — Split list into evenly sized chunks
- `run_batches(func, all_tasks, chunk_size=20, delay=0.5)` — Execute tasks in sequential batches with delay (rate-limiting)

**Modes:**
- `mode="thread"` — For I/O-bound tasks (API calls, file I/O)
- `mode="process"` — For CPU-bound tasks (data processing, computation)

---

## C17 — API Violations (MAJOR) ✅

**Rule:** Use C17 for all REST API calls. Never use requests library directly.

### Direct Requests Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `requests.get(` | MAJOR | `get_json(url, headers, params)` from C17 |
| `requests.post(` | MAJOR | `post_json(url, json_data, headers)` from C17 |
| `requests.put(` | MAJOR | `api_request("PUT", url, ...)` from C17 |
| `requests.delete(` | MAJOR | `api_request("DELETE", url, ...)` from C17 |
| `requests.request(` | MAJOR | `api_request(method, url, ...)` from C17 |
| `import requests` then direct use | MAJOR | Use C17 functions (requests is in C00) |

### Request Handling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual retry loop for API calls | MAJOR | `api_request(..., retries=3)` from C17 |
| Manual timeout handling | MAJOR | `api_request(..., timeout=15)` from C17 |
| `try: requests.get(...) except Timeout:` | MAJOR | `api_request(...)` from C17 (handles timeouts) |
| `time.sleep()` between API retries | MAJOR | `api_request(..., retries=N)` from C17 (has backoff) |

### Response Handling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `response.json()` after requests call | MINOR | `get_json(url)` returns parsed JSON directly |
| `if response.ok: return response.json()` | MINOR | `get_json(url)` or `post_json(url, data)` from C17 |

### Authentication Header Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `{"Authorization": f"Bearer {token}"}` | MINOR | `get_auth_header(token, bearer=True)` from C17 |
| `{"Authorization": token}` | MINOR | `get_auth_header(token, bearer=False)` from C17 |
| Manual auth header construction | MINOR | `get_auth_header(token)` from C17 |

### Legacy HTTP Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `urllib.request.urlopen(` | MAJOR | `api_request(...)` from C17 |
| `urllib.request.Request(` | MAJOR | `api_request(...)` from C17 |
| `http.client.HTTPConnection(` | MAJOR | `api_request(...)` from C17 |

**Available Functions:**
- `api_request(method, url, headers, params, data, json_data, retries=3, timeout=15)` — Generic REST request with retry/timeout
- `get_json(url, headers, params)` — GET request returning parsed JSON
- `post_json(url, json_data, headers)` — POST request with JSON body returning parsed JSON
- `get_auth_header(token, bearer=True)` — Build Authorization header

---

## C18 — Web Automation Violations (MAJOR) ✅

**Rule:** Use C18 for all browser automation. Never use Selenium WebDriver directly.

### Driver Setup Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `webdriver.Chrome(` | MAJOR | `get_chrome_driver(profile_name, headless)` from C18 |
| `webdriver.Chrome(options=...)` | MAJOR | `get_chrome_driver(headless=True/False)` from C18 |
| `webdriver.Firefox(` | MAJOR | Contact owner — only Chrome supported |
| `webdriver.Edge(` | MAJOR | Contact owner — only Chrome supported |
| `ChromeOptions()` manual configuration | MAJOR | `get_chrome_driver()` from C18 (pre-configured) |
| Manual Chrome profile path handling | MAJOR | `get_chrome_driver(profile_name="Default")` from C18 |

### Element Waiting Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `WebDriverWait(driver, timeout).until(` | MINOR | `wait_for_element(driver, by, selector, timeout)` from C18 |
| `EC.presence_of_element_located(` | MINOR | `wait_for_element(driver, by, selector)` from C18 |
| `EC.element_to_be_clickable(` | MINOR | `wait_for_element(driver, by, selector)` from C18 |
| `driver.find_element(By.` | MINOR | `wait_for_element(driver, by, selector)` from C18 (safer) |
| `driver.find_elements(By.` | MINOR | `wait_for_element(...)` from C18 |

### Element Interaction Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `element.click()` without wait | MINOR | `click_element(driver, by, selector)` from C18 |
| Manual element locate + click | MINOR | `click_element(driver, by, selector)` from C18 |

### Scrolling Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")` | MINOR | `scroll_to_bottom(driver, pause_time)` from C18 |
| Manual scroll-to-bottom loop | MINOR | `scroll_to_bottom(driver)` from C18 |
| Lazy-loading scroll logic | MINOR | `scroll_to_bottom(driver, pause_time=1.0)` from C18 |

### Driver Shutdown Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `driver.quit()` | MINOR | `close_driver(driver)` from C18 |
| `driver.close()` | MINOR | `close_driver(driver)` from C18 |
| Manual WebDriver cleanup | MINOR | `close_driver(driver)` from C18 |

**Available Functions:**
- `get_chrome_driver(profile_name=None, headless=False)` — Create configured Chrome WebDriver
- `wait_for_element(driver, by, selector, timeout=10)` — Wait for element by locator strategy
- `scroll_to_bottom(driver, pause_time=1.0)` — Scroll to bottom with lazy-loading support
- `click_element(driver, by, selector)` — Safely locate and click element
- `close_driver(driver)` — Clean WebDriver shutdown

**Locator Strategies (by parameter):**
- `"id"`, `"name"`, `"xpath"`, `"css_selector"`, `"class_name"`, `"tag_name"`, `"link_text"`, `"partial_link_text"`

---

## C19 — Google Drive Violations (MAJOR) ✅

**Rule:** Use C19 for all Google Drive operations — both local drive detection and API access.

### Local Drive Detection Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Manual check for Google Drive App installation | MINOR | `is_google_drive_installed()` from C19 |
| Manual enumeration of drive letters for Google Drive | MINOR | `get_google_drive_accounts()` from C19 |
| `Path("H:/My Drive/...")` with hardcoded drive letter | MINOR | Use `get_google_drive_accounts()` to find root dynamically |
| `str(path).split("/")[0]` for drive root extraction | MINOR | `extract_drive_root(path)` from C19 |

### API Authentication Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `build('drive', 'v3', credentials=...)` | MAJOR | `get_drive_service()` from C19 |
| `InstalledAppFlow.from_client_secrets_file(` | MAJOR | `get_drive_service()` from C19 (handles OAuth) |
| `Credentials.from_authorized_user_file(` | MAJOR | `get_drive_service()` from C19 (handles token) |
| `creds.refresh(Request())` | MAJOR | `get_drive_service()` from C19 (handles refresh) |
| Manual OAuth token management | MAJOR | `get_drive_service()` from C19 |

### File/Folder Search Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `service.files().list(q="mimeType='...folder'")` | MINOR | `find_folder_id(service, folder_name)` from C19 |
| `service.files().list(q="name='...'")` | MINOR | `find_file_id(service, file_name, in_folder_id)` from C19 |
| Manual Drive file search queries | MINOR | `find_file_id(service, name)` from C19 |
| Manual Drive folder search queries | MINOR | `find_folder_id(service, name)` from C19 |

### File Upload Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `MediaFileUpload(local_path, resumable=True)` | MINOR | `upload_file(service, local_path, folder_id)` from C19 |
| `service.files().create(body=..., media_body=...)` | MINOR | `upload_file(service, path, folder_id, filename)` from C19 |
| `MediaIoBaseUpload(...)` for DataFrame upload | MINOR | `upload_dataframe_as_csv(service, csv_buffer, filename, folder_id)` from C19 |

### File Download Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `MediaIoBaseDownload(fh, request)` | MINOR | `download_file(service, file_id, local_path)` from C19 |
| `service.files().get_media(fileId=...)` | MINOR | `download_file(service, file_id, local_path)` from C19 |
| Manual chunked download loop | MINOR | `download_file(service, file_id, path)` from C19 |

**Available Functions:**
- **Constants:** `SCOPES` (Google Drive API scopes)
- **Local Detection:** `is_google_drive_installed()`, `get_google_drive_accounts()`, `extract_drive_root(path)`
- **API Auth:** `get_drive_service()` — handles OAuth, token refresh, service creation
- **Search:** `find_folder_id(service, folder_name)`, `find_file_id(service, file_name, in_folder_id=None)`
- **Upload:** `upload_file(service, local_path, folder_id, filename)`, `upload_dataframe_as_csv(service, csv_buffer, filename, folder_id)`
- **Download:** `download_file(service, file_id, local_path)`

**Note:** Uses `GDRIVE_CREDENTIALS_FILE` and `GDRIVE_TOKEN_FILE` from C02 for OAuth credential storage.

---

## C20 — GUI Helper Violations (MINOR) ✅

**Rule:** Use C20 for simple GUI popups and thread-safe task execution (outside main GUI framework).

### Message Popup Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `messagebox.showinfo(title, message)` | MINOR | `show_info(message, title)` from C20 |
| `messagebox.showwarning(title, message)` | MINOR | `show_warning(message, title)` from C20 |
| `messagebox.showerror(title, message)` | MINOR | `show_error(message, title)` from C20 |
| Manual `tk.Tk(); root.withdraw(); messagebox...` pattern | MINOR | Use C20 functions (handle root window internally) |

### Progress Popup Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `ttk.Progressbar(` for modal progress | MINOR | `ProgressPopup(parent, message)` from C20 |
| Manual progress window with grab_set() | MINOR | `ProgressPopup(parent, message)` from C20 |
| Manual progress percentage update | MINOR | `popup.update_progress(current, total)` from C20 |

### Threading Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `threading.Thread(target=func, daemon=True).start()` | MINOR | `run_in_thread(func, *args, **kwargs)` from C20 |
| Manual thread creation with exception handling | MINOR | `run_in_thread(target, *args)` from C20 |

### Theme/Style Violations

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| Hardcoded colours like `"#F8F9FA"`, `"#212529"` | MINOR | Use `GUI_THEME["bg"]`, `GUI_THEME["fg"]` from C20 |
| Hardcoded fonts like `("Segoe UI", 10)` | MINOR | Use `GUI_THEME["font"]`, `GUI_THEME["font_bold"]` from C20 |

**Available Functions:**
- **Constants:** `GUI_THEME` (dict with bg, fg, accent, success, warning, error, font, font_bold)
- **Popups:** `show_info(message, title)`, `show_warning(message, title)`, `show_error(message, title)`
- **Progress:** `ProgressPopup(parent, message)` — context manager with `update_progress(current, total)`
- **Threading:** `run_in_thread(target, *args, **kwargs)` — returns daemon Thread with exception logging

**Note:** C20 imports GUI packages from `gui.G00a_gui_packages`, not directly from tkinter. This is allowed as C20 is a GUI helper module.

---

## GUI — Tkinter Import Violations (CRITICAL)

**Rule:** GUI pages (Gx0+) import from G02a facade only, never directly from tkinter.

| Detection Pattern | Severity | Use Instead |
|-------------------|----------|-------------|
| `import tkinter` | CRITICAL | `from gui.G02a_widget_primitives import ...` |
| `from tkinter import` | CRITICAL | `from gui.G02a_widget_primitives import ...` |
| `import tk` | CRITICAL | `from gui.G02a_widget_primitives import ...` |
| `from tkinter import ttk` | CRITICAL | `from gui.G02a_widget_primitives import ...` |
| `ttk.Button(` | CRITICAL | `make_button(parent, ...)` from G02a |
| `ttk.Label(` | CRITICAL | `make_label(parent, ...)` from G02a |
| `ttk.Entry(` | CRITICAL | `make_entry(parent, ...)` from G02a |
| `ttk.Frame(` | CRITICAL | `make_frame(parent, ...)` from G02a |
| `ttk.Combobox(` | CRITICAL | `make_combobox(parent, ...)` from G02a |
| `tk.StringVar(` | CRITICAL | `StringVar` from G02a |
| `tk.BooleanVar(` | CRITICAL | `BooleanVar` from G02a |
| `from gui.G00a_gui_packages import` (in Gx0+) | CRITICAL | `from gui.G02a_widget_primitives import ...` |
| `from gui.G01` (in Gx0+) | CRITICAL | `from gui.G02a_widget_primitives import ...` |

**Exception:** G00–G04 framework modules may import from G00a directly.

---

## Structural Violations (CRITICAL)

**Rule:** Section structure must match template exactly.

| Detection Pattern | Severity | Issue |
|-------------------|----------|-------|
| Missing `from __future__ import annotations` | CRITICAL | Section 1 incomplete |
| Missing `sys.dont_write_bytecode = True` | CRITICAL | Section 1 incomplete |
| Missing `from core.C00_set_packages import *` | CRITICAL | Section 2 incomplete |
| Missing `logger = get_logger(__name__)` | CRITICAL | No logger initialised |
| Missing `__all__ = [` | MAJOR | Section 98 missing |
| Missing `def main()` | MAJOR | Section 99 incomplete |
| Missing `if __name__ == "__main__":` | MAJOR | Section 99 incomplete |
| Missing `init_logging()` in main block | MAJOR | Logging not initialised |
| Code outside Section 99 that executes at import | CRITICAL | Side-effects at import time |
| Function calls at module level | CRITICAL | Side-effects at import time |

---

## 🆕 ADDITIONS FROM SCRIPT REVIEW

*This section will be populated as we review each core script*

---

## Quick Self-Check

Before delivering code, verify these are NOT present:

```
□ Any direct import statement (use C00 — only sys/Path exception in Section 1)
□ print( (use logger from C01)
□ from logging import DEBUG/INFO/WARNING/ERROR (use from C01)
□ logging.basicConfig / logging.FileHandler (use init_logging from C01)
□ Path(__file__).parent.parent (use PROJECT_ROOT from C02)
□ os.makedirs / path.mkdir( (use ensure_directory from C02)
□ Hardcoded "/data/", "/outputs/", "/config/", "/logs/" (use C02 constants)
□ tempfile.mkstemp / tempfile.mktemp (use get_temp_file from C02)
□ platform.system() / sys.platform (use detect_os from C03)
□ yaml.safe_load(open(...)) for config (use get_config from C04)
□ sys.exit(1) on error (use handle_error(e, fatal=True) from C05)
□ os.path.exists / .isfile / .is_dir (use file_exists/dir_exists from C06)
□ if col not in df.columns (use validate_required_columns from C06)
□ datetime.now() / date.today() / .strftime( / .strptime( (use C07)
□ pd.read_csv / df.to_csv / json.load / json.dump (use C09)
□ pd.merge / df.drop_duplicates / df.fillna (prefer C12 for logged wrappers - MINOR)
□ requests.get / requests.post (use C17)
□ ThreadPoolExecutor / ProcessPoolExecutor (use C16)
□ pdfplumber.open / PdfReader / PdfWriter (use C10)
□ zipfile.ZipFile for backups / manual timestamped copies (use C11)
□ snowflake.connector.connect / cursor.execute for Snowflake (use C14)
□ ttk.Button / ttk.Label / ttk.Frame in Gx0+ (use G02a factories)
```

---

## Integration with A03 Audit

When running A03 audit, check:

1. **CRITICAL violations:** Any match = FAIL, must fix
2. **MAJOR violations:** Any match = FAIL, must fix  
3. **MINOR violations:** Note in response, fix if time permits

**Pass criteria:** Zero CRITICAL, zero MAJOR violations.

---

**This document is the authoritative reference for Core function replacement patterns.**